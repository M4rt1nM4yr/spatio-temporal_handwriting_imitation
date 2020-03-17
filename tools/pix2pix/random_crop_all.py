#!/usr/bin/env python

import argparse
import os
import random

from PIL import Image

from algorithms.image_cut_and_fill import cutSingleImage


def loadInputDataset(input, minSize):

    print("Loading dataset ...")

    fileNames = list([f for f in os.listdir(input) if os.path.isfile(os.path.join(input, f))])
    fileNames.sort()

    dataset = list()

    for fileNum, fileName in enumerate(fileNames):
        #print(fileNum, "/", len(fileNames), "   ", fileName)
        img = Image.open(os.path.join(input, fileName))

        width, height = img.size

        if height < minSize or width < minSize:
            #print("    Too small, skipping.")
            continue

        dataset.append(img)

    return dataset


def createRandom256Img(inputDataset, appendSecond):

    inputSample = random.choice(inputDataset)
    newImage = cutSingleImage((256, 256), inputSample)

    if appendSecond:
        resultImage = Image.new("RGB", (512, 256), (255, 255, 255))
        resultImage.paste(newImage)
    else:
        resultImage = newImage

    if False:
        resultImage.show()
        exit(1)

    return resultImage


def main():

    parser = argparse.ArgumentParser(description='Converts the CVL dataset to a skeleton version.')
    parser.add_argument('input', help='The A side input folder')
    parser.add_argument('output', help='The output folder for pix2pix training')
    parser.add_argument('--samples', type=int, default=10000, help='The number of samples to generate')
    parser.add_argument('--min-size', type=int, default=0, help='The minimum size of the input images')
    parser.add_argument('--pix2pix', action='store_true', help='Appends a second white image to the right to make it pix2pix input compatible')
    args = parser.parse_args()


    print(args)

    inputDataset = loadInputDataset(args.input, args.min_size)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    random.seed(42)
    for i in range(args.samples):
        img = createRandom256Img(inputDataset, args.pix2pix)
        img.save(os.path.join(args.output, str(i) + '.png'))


if __name__ == "__main__":
    main()
