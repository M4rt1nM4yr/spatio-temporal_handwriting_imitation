from datastructures.PenPosition import PenPosition


def sample_to_penpositions(strokes, char_labels, eoc_labels, bow_labels):
    penPositions = list()

    for strokeId, stroke in enumerate(strokes):
        penPositions.append(PenPosition(stroke[0],
                                        stroke[1],
                                        stroke[2],
                                        char_labels[strokeId],
                                        eoc_labels[strokeId],
                                        bow_labels[strokeId]))

    return penPositions
