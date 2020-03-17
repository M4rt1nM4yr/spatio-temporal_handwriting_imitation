#!/usr/bin/env python3

import argparse
import os

from PIL import Image

from algorithms.image_cut_and_fill import generateCutOffset, cutImageWithOffset

from tqdm import tqdm

import json


def findSmallestMultipleOf(num, multiplier):
    numInt = int(num)
    multiplierInt = int(multiplier)

    numberOfTimes = (numInt-1)//multiplierInt
    return (numberOfTimes+1)*multiplierInt


def processImages(imgA, imgB, outSize):
    width, height = imgA.size

    if outSize:
        outWidth, outHeight = outSize
    else:
        outWidth = findSmallestMultipleOf(width, 256)
        outHeight = findSmallestMultipleOf(height, 256)

    outImg = Image.new("RGB", (2*outWidth, outHeight), (255, 255, 255))

    cutOffset = generateCutOffset((outWidth, outHeight), (width, height))

    outImgA = cutImageWithOffset((outWidth, outHeight), imgA, cutOffset)
    outImg.paste(outImgA, (0, 0))

    if imgB:
        outImgB = cutImageWithOffset((outWidth, outHeight), imgB, cutOffset)
        outImg.paste(outImgB, (outWidth, 0))

    return outImg, {'offset': cutOffset, 'size': (width, height)}


def main():

    parser = argparse.ArgumentParser(description='Resizes all inputs to multiples of 256 and adds a white area to the right, preparing the data for pix2pix inference.')
    parser.add_argument('--inputB', default=None, help='The B side input folder')
    parser.add_argument('--out-size', nargs=2, type=int, default=None, metavar=('SIZE_X', 'SIZE_Y'), help='The size of the generated images.')
    parser.add_argument('--min-size', type=int, default=0, help='The minimum size of the input images')
    parser.add_argument('inputA', help='The A side input folder')
    parser.add_argument('output', help='The output folder for pix2pix training')
    args = parser.parse_args()

    print(args)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    metaData = {}

    fileNames = set([f for f in os.listdir(args.inputA) if os.path.isfile(os.path.join(args.inputA, f))])
    for fileName in tqdm(fileNames):
        fileNameA = os.path.join(args.inputA, fileName)

        imgA = Image.open(fileNameA)
        imgB = None

        if imgA.size[0] < args.min_size or imgA.size[1] < args.min_size:
            continue

        if args.inputB:
            fileNameB = os.path.join(args.inputB, fileName)
            if os.path.isfile(fileNameB):
                imgB = Image.open(fileNameB)
                if imgA.size != imgB.size:
                    print('\n', imgA.size, imgB.size)
                assert(imgA.size == imgB.size)

        imgOut, cropInfo = processImages(imgA, imgB, args.out_size)
        imgOut.save(os.path.join(args.output, fileName))

        metaData[fileName] = cropInfo

    with open(os.path.join(args.output, 'metadata.json'), 'w') as metaDataFile:
        json.dump(metaData, metaDataFile, sort_keys=True, indent=4)



if __name__ == "__main__":
    main()
