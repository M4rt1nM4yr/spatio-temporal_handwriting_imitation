#!/usr/bin/env python3

import argparse
import os

from PIL import Image

import random

from algorithms.image_cut_and_fill import cutAndJoinDualImages

from tqdm import tqdm

def loadInputDataset(inputA, inputB, minSize):

    print("Loading dataset ...")

    fileNamesA = set([f for f in os.listdir(inputA) if os.path.isfile(os.path.join(inputA, f))])

    if inputB:
        fileNamesB = set([f for f in os.listdir(inputB) if os.path.isfile(os.path.join(inputB, f))])
        fileNames = fileNamesA.intersection(fileNamesB)
    else:
        fileNames = fileNamesA

    dataset = list()

    for fileNum, fileName in enumerate(fileNames):
        #print(fileNum, "/", len(fileNames), "   ", fileName)
        imgA = Image.open(os.path.join(inputA, fileName))
        if inputB:
            imgB = Image.open(os.path.join(inputB, fileName))
        else:
            imgB = Image.new("RGB", imgA.size, (255,255,255))

        widthA, heightA = imgA.size
        widthB, heightB = imgB.size
        assert(widthA == widthB)
        assert(heightA == heightB)

        if heightA < minSize or widthA < minSize:
            #print("    Too small, skipping.")
            continue

        dataset.append((imgA, imgB))

    return dataset


def randomPos(outputSize, inputSize):

    if outputSize > inputSize:
        return random.randrange(outputSize-inputSize)
    else:
        return random.randint(outputSize - inputSize, 0)


def createRandomImg(inputDataset, outputSize, unaligned=False):

    inputSample1, inputSample2 = random.choice(inputDataset)

    if unaligned:
        _, inputSample2 = random.choice(inputDataset)

    #print(inputSample)

    #inputSample[0].show()
    #inputSample[1].show()

    newImage = cutAndJoinDualImages(outputSize, inputSample1, inputSample2, unaligned=unaligned)

    if False:
        newImage.show()
        exit(1)

    return newImage


def main():

    parser = argparse.ArgumentParser(description='Converts the CVL dataset to a skeleton version.')
    parser.add_argument('inputA', help='The A side input folder')
    parser.add_argument('--inputB', default=None, help='The B side input folder')
    parser.add_argument('output', help='The output folder for pix2pix training')
    parser.add_argument('--samples', type=int, default=10000, help='The number of samples to generate')
    parser.add_argument('--min-size', type=int, default=0, help='The minimum size of the input images')
    parser.add_argument('--out-size', nargs=2, type=int, default=[256, 256], metavar=('SIZE_X', 'SIZE_Y'), help='The size of the generated images')
    parser.add_argument('--unaligned', action='store_true', help='Disables the alignment between images. For style transfer tests.')
    args = parser.parse_args()

    print(args)

    inputDataset = loadInputDataset(args.inputA, args.inputB, args.min_size)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    for i in tqdm(range(args.samples)):
        img = createRandomImg(inputDataset, args.out_size, args.unaligned)
        img.save(os.path.join(args.output, str(i) + '.png'))


if __name__ == "__main__":
    main()
