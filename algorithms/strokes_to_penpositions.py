from datastructures.PenPosition import PenPosition


def strokes_to_penpositions(strokes):
    penPositions = list()

    seenBows = {0}

    for strokeId in strokes.strokeOrder:
        stroke = strokes.getStroke(strokeId)
        for strokePoint in stroke.points:
            bowLabel = 0.0
            if strokePoint.bowLabel not in seenBows:
                bowLabel = 1.0
                seenBows.add(strokePoint.bowLabel)

            penPosition = PenPosition(strokePoint.pos[0],
                                      strokePoint.pos[1],
                                      0.0,
                                      strokePoint.charLabel,
                                      strokePoint.eocLabel,
                                      bowLabel)
            penPositions.append(penPosition)
        penPositions[-1].penUp = 1.0

    seenEocs = {0}
    for penPosition in reversed(penPositions):
        eocLabel = 0.0
        if penPosition.eocLabel not in seenEocs:
            eocLabel = 1.0
            seenEocs.add(penPosition.eocLabel)
        penPosition.eocLabel = eocLabel

    return penPositions
