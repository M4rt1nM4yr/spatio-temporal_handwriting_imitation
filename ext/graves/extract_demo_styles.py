#!/usr/bin/env python3

import numpy as np

import svgwrite
import drawing

import os
import argparse

style_ids = [0, 5, 8, 12, 19, 26, 28, 32, 37, 42, 44, 46, 51]

parser = argparse.ArgumentParser(description='Extracts demo styles from the dataset')
parser.add_argument('dataset', help='The dataset folder.')
args = parser.parse_args()
print(args)


database_x = np.load(os.path.join(args.dataset, "x.npy"))
database_x_len = np.load(os.path.join(args.dataset, "x_len.npy"))
database_c = np.load(os.path.join(args.dataset, "c.npy"))
database_c_len = np.load(os.path.join(args.dataset, "c_len.npy"))


for styleId, databaseId in enumerate(style_ids):
    x = database_x[databaseId]
    x_len = database_x_len[databaseId]
    c_raw = database_c[databaseId]
    c_len = database_c_len[databaseId]

    x = x[:x_len-1]
    c = drawing.decode_ascii(c_raw, c_len).encode('utf-8')

#    print("===========", styleId, "============")
#    print(c)
#    print(x)

    np.save("styles/style-" + str(styleId) + "-chars.npy", c)
    np.save("styles/style-" + str(styleId) + "-strokes.npy", x)

    x = drawing.offsets_to_coords(x)
    x_max = np.max(x, axis=0).astype(int)[:2] + 10
    x_min = np.min(x, axis=0).astype(int)[:2] - 10
    print(x_min, x_max)

    offset = - x_min
    size = x_max - x_min
    zoomFactor = 2

    svg = svgwrite.Drawing('styles/style-' + str(styleId) + '.svg',
                           profile='tiny',
                           size=(str(zoomFactor*size[0]) + 'px', str(zoomFactor*size[1]) + 'px'))

    svg.add(svg.rect(size=('100%','100%'), fill='white'))

    points = list()
    for pX_raw, pY_raw, penUp in x:
        pX = pX_raw + offset[0]
        pY = size[1] - (pY_raw + offset[1])
        points.append((zoomFactor*pX,zoomFactor*pY))
        if penUp:
            print(points)
            svg.add(svg.polyline(points, fill='none', stroke='black'))
            points = list()
    if points:
        svg.add(svg.polyline(points, fill='none', stroke='black'))

    svg.save()


# Open database
chars = np.load("styles/style-8-chars.npy")
strokes = np.load("styles/style-8-strokes.npy")


print("=========== Existing ============")
print(chars)
print(strokes)
