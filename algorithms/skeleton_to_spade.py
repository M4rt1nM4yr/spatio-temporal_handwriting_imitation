import matplotlib.pyplot as plt

import numpy as np

from algorithms.thicken_lines import thicken_lines
from PIL import Image, ImageOps

from pipeline.skeletonization import Skeletonizer

import argparse


def skeleton_to_spade(skeleton):
    return Image.fromarray(thicken_lines(np.asarray(skeleton), 6).astype('uint32')).convert('RGB')


def main():
    parser = argparse.ArgumentParser(description='Converts normal skeletons to spade skeletons')
    parser.add_argument('input', help='The input skeleton image')
    parser.add_argument('output', help='The output spade skeleton image')
    parser.add_argument('--deblur', action='store_true',
                        help='Adds a deblurring to the skeleton input images')
    args = parser.parse_args()

    skeleton = ImageOps.invert(Image.open(args.input).convert('L'))

    if args.deblur:
        skeleton = Skeletonizer.skeletonize_sharp(skeleton)

    spadeSkeleton = skeleton_to_spade(skeleton)

    skeleton.show()
    spadeSkeleton.show()
    Image.fromarray(np.asarray(spadeSkeleton)*255).show()

    spadeSkeleton.save(args.output)


if __name__ == "__main__":
    main()
