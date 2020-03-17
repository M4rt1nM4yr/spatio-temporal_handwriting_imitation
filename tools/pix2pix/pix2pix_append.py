#!/usr/bin/env python3

import argparse
import os
import sys

from PIL import Image

from tqdm import tqdm

from multiprocessing import Pool


def processImage(inputA, inputB, fileName, output):
    imgA = Image.open(os.path.join(inputA, fileName))

    if inputB:
        imgB = Image.open(os.path.join(inputB, fileName))
    else:
        imgB = Image.new("RGB", imgA.size, (255, 255, 255))

    widthA, heightA = imgA.size
    widthB, heightB = imgB.size
    assert (widthA == widthB)
    assert (heightA == heightB)

    img = Image.new("RGB", (imgA.size[0] * 2, imgA.size[1]), (255, 255, 255))
    img.paste(imgA)
    img.paste(imgB, (imgA.size[0], 0))

    img.save(os.path.join(output, fileName))


def processInputDataset(inputA, inputB, output):

    print("Processing dataset ...")

    fileNamesA = set([f for f in os.listdir(inputA) if os.path.isfile(os.path.join(inputA, f))])

    if inputB:
        fileNamesB = set([f for f in os.listdir(inputB) if os.path.isfile(os.path.join(inputB, f))])
        fileNames = fileNamesA.intersection(fileNamesB)
    else:
        fileNames = fileNamesA

    with Pool() as pool:

        tasks = list()

        for fileName in tqdm(fileNames, desc="Creating tasks"):
            tasks.append(pool.apply_async(processImage, (inputA, inputB, fileName, output)))

        for task in tqdm(tasks, desc="Waiting for tasks to complete"):
            task.wait()


def main():

    parser = argparse.ArgumentParser(description='Converts the CVL dataset to a skeleton version.')
    parser.add_argument('inputA', help='The A side input folder')
    parser.add_argument('--inputB', default=None, help='The B side input folder')
    parser.add_argument('output', help='The output folder for pix2pix training')
    args = parser.parse_args()

    print(args)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    processInputDataset(args.inputA, args.inputB, args.output)


if __name__ == "__main__":
    main()
