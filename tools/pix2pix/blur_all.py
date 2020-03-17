#!/usr/bin/env python3

import argparse
import os

from PIL import Image, ImageFilter


def main():

    parser = argparse.ArgumentParser(description='Blurres all images in folder with a gaussian of 1.')
    parser.add_argument('input', help='The input dataset folder')
    parser.add_argument('output', help='The output database folder')
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    fileNames = [f for f in os.listdir(args.input) if os.path.isfile(os.path.join(args.input, f))]
    for fileNum, relativeFilename in enumerate(fileNames):
        inFile = os.path.join(args.input, relativeFilename)
        if not os.path.isfile(inFile):
            continue
        outFile = os.path.join(args.output, relativeFilename)

        img = Image.open(inFile)
        img = img.filter(ImageFilter.GaussianBlur(1))
        img.save(outFile)

        print(fileNum, "/", len(fileNames), "  ", relativeFilename)


if __name__ == "__main__":
    main()
