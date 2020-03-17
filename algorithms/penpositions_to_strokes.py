from datastructures import StrokesGraph


def penpositions_to_strokes(penPositions):
    strokes = StrokesGraph.StrokesGraph()

    currentStrokeData = list()

    totalNumEocs = [penPosition.eocLabel > 0.5 for penPosition in penPositions].count(True)

    # Count eocs down instead of up, otherwise we would miss an eoc on the very end
    numEocsSeen = totalNumEocs
    numBowsSeen = 0

    for penPosition in penPositions:
        if penPosition.bowLabel > 0.5:
            numBowsSeen += 1
        point = StrokesGraph.StrokePoint(penPosition.pos, numEocsSeen, numBowsSeen, penPosition.charLabel)
        currentStrokeData.append(point)
        if penPosition.eocLabel > 0.5:
            numEocsSeen -= 1
        if penPosition.penUp > 0.5:
            strokes.addStroke(currentStrokeData)
            currentStrokeData = list()

    if currentStrokeData:
        strokes.addStroke(currentStrokeData)

    strokes.checkForConsistency()
    return strokes
