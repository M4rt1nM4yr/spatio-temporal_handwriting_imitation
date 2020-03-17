import os

from utils import add_path
import numpy as np
from skimage import morphology

from PIL import Image

import gc

from algorithms.image_padding import pad_image, unpad_image

with add_path(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ext', 'pix2pix')):
    from options.test_options import TestOptions
    from models import create_model
    from data.single_item_dataset import SingleItemDataset
    from util.util import tensor2im


class Skeletonizer:

    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.pix2pixDir = os.path.join(self.dir_path, '..', 'ext', 'pix2pix')

        self.opts = TestOptions().parse(['--dataroot', '',
                                   '--model', 'pix2pix',
                                   '--checkpoints_dir',
                                   str(os.path.join(self.dir_path,'..', 'checkpoints', 'pix2pix')),
                                   '--name', 'cvl_skeletonization_scalable'
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

    def __createSingleImageDataset(self, img):
        with add_path(self.pix2pixDir):
            dataset = SingleItemDataset(self.opts, img)
            return dataset

    def skeletonize_blurred(self, img):

        # print(img.size)
        img, imgResizeParams = pad_image(img, 256)

        dataset = self.__createSingleImageDataset(img)

        self.model.set_input(dataset[0])
        self.model.test()
        visuals = self.model.get_current_visuals()

        result_img_array = tensor2im(visuals['fake_B'])

        result_img = Image.fromarray(result_img_array)

        return unpad_image(result_img, imgResizeParams)

    @staticmethod
    def skeletonize_sharp(img, threshold=215, return_threshold_img=False):

        img = np.asarray(img)

        if img.ndim > 2:
            bw = np.mean(img, axis=2)
        else:
            bw = img

        threshold_img = bw < threshold

        skeleton_img = morphology.thin(threshold_img)

        if return_threshold_img:
            return skeleton_img, threshold_img
        else:
            return skeleton_img

    def skeletonize(self, img):
        blurred = self.skeletonize_blurred(img)
        return self.skeletonize_sharp(blurred)
