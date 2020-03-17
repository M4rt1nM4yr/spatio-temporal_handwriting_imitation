import os

from utils import add_path
import numpy as np
from skimage import morphology
from PIL import Image

from algorithms.image_padding import pad_image, unpad_image
from pipeline.render_skeleton import blur_skeleton

import gc
import argparse

with add_path(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ext', 'pix2pix')):
    from options.test_options import TestOptions
    from models import create_model
    from data.single_item_dataset import SingleItemDataset
    from util.util import tensor2im


class PenStyleTransfer:

    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.pix2pixDir = os.path.join(self.dir_path, '..', 'ext', 'pix2pix')

        netName = 'cond_pix2pix_2048_asymmetric'

        self.opts = TestOptions().parse(['--dataroot', '',
                                   '--model', 'cond_pix2pix',
                                   '--checkpoints_dir',
                                   str(os.path.join(self.dir_path,'..', 'checkpoints', 'pix2pix')),
                                   '--name', netName
                                   ])  # set model options
        # hard-code some parameters
        self.opts.num_threads = 0  # test code only supports num_threads = 1
        self.opts.batch_size = 1  # test code only supports batch_size = 1
        self.opts.preprocess = 'none'
        self.opts.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
        self.opts.no_flip = True  # no flip; comment this line if results on flipped images are needed.
        self.opts.display_id = -1  # no visdom display; the test code saves the results to a HTML file.

        self.model = create_model(self.opts)  # create a model given opt.model and other options
        self.model.setup(self.opts)  # regular setup: load and print networks; create schedulers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
        del self.opts
        gc.collect()

    def __createSingleImageDataset(self, img, style):
        with add_path(self.pix2pixDir):
            dataset = SingleItemDataset(self.opts, img, style)
            return dataset

    def transferStyle(self, skeletonImg, styleImg):

        skeletonImg, imgResizeParams = pad_image(skeletonImg, (2048, 256))
        styleImg, _ = pad_image(styleImg, (2048, 256))

        dataset = self.__createSingleImageDataset(skeletonImg, styleImg)

        self.model.set_input(dataset[0])
        self.model.test()
        visuals = self.model.get_current_visuals()

        result_img_array = tensor2im(visuals['fake_B'])

        result_img = Image.fromarray(result_img_array)

        return unpad_image(result_img, imgResizeParams)



def readFilesList(fileOrFolder):
    if os.path.isfile(fileOrFolder):
        dirname, filename = os.path.split(fileOrFolder)
        return dirname, [filename]
    elif os.path.isdir(fileOrFolder):
        return fileOrFolder, [f for f in os.listdir(fileOrFolder) if os.path.isfile(os.path.join(fileOrFolder, f))]


def main():
    parser = argparse.ArgumentParser(description='Does a style transfer from a style image to a skeleton image')
    parser.add_argument('input', help='The input skeleton image/folder')
    parser.add_argument('style', help='The input style image/folder')
    parser.add_argument('--output', help='The output image/folder')
    parser.add_argument('--dont-blur', action='store_true', help='Omits the blurring. Used for already blurred skeleton images.')
    args = parser.parse_args()
    print(args)

    input_folder, input_files = readFilesList(args.input)
    style_folder, style_files = readFilesList(args.style)

    with PenStyleTransfer(colored=False) as penStyleTransfer:
        for style_filename in style_files:
            styleImg = Image.open(os.path.join(style_folder, style_filename))
            for input_filename in input_files:
                skeletonImg = Image.open(os.path.join(input_folder, input_filename)).convert('RGB')

                skeletonImgName, _ = os.path.splitext(input_filename)

                if not args.dont_blur:
                    skeletonImg = blur_skeleton(skeletonImg)

                result = penStyleTransfer.transferStyle(skeletonImg, styleImg)

                if args.output is not None:
                    if os.path.isdir(args.output):
                        result.save(os.path.join(args.output, skeletonImgName + style_filename))
                    elif not os.path.isfile(args.output) and not os.path.splitext(args.output)[1]:
                        os.makedirs(args.output)
                        result.save(os.path.join(args.output, skeletonImgName + style_filename))
                    else:
                        result.save(args.output)
                else:
                    styleImg.show()
                    skeletonImg.show()
                    result.show()


if __name__ == "__main__":
    main()
