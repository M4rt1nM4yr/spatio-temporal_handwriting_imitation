#!/usr/bin/env python3

import argparse
import os

from PIL import Image

from tqdm import tqdm

import json


def main():

    parser = argparse.ArgumentParser(description='Takes pix2pix results and converts them back to their original size, based on the given metadata.')
    parser.add_argument('input', help='The pix2pix results folder')
    parser.add_argument('metadata', default=None, help='The metadata.json file')
    parser.add_argument('output', help='The output folder')
    args = parser.parse_args()

    print(args)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    with open(args.metadata, 'r') as metaDataFile:
        metaData = json.load(metaDataFile)

    fileNames = set([f for f in os.listdir(args.input) if os.path.isfile(os.path.join(args.input, f))])
    for fileName in tqdm(fileNames):
        fileNameA = os.path.join(args.input, fileName)

        img = Image.open(fileNameA)
        metaInfo = metaData[fileName]

        offset = metaInfo['offset']
        size = metaInfo['size']
        imgOut = img.crop((offset[0], offset[1], offset[0]+size[0], offset[1]+size[1]))

        imgOut.save(os.path.join(args.output, fileName))


if __name__ == "__main__":
    main()
