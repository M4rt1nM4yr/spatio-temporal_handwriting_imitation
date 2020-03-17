import logging
import os
import gc

import numpy as np

from utils import add_path

from datastructures.PenPosition import PenPosition

with add_path(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ext', 'graves')):
    import drawing
    from rnn import rnn


def preprocess(sampleStrokes):

    strokes = sampleStrokes

    coords = []
    if strokes[0].penUp < 0.5:
        coords = [[0, 0, 1]]

    for i, point in enumerate(strokes):
        coords.append([
            int(point.pos[0]),
            -1*int(point.pos[1]),
            point.penUp
        ])
    coords = np.array(coords)

    coords = drawing.align(coords)
    coords = drawing.denoise(coords)
    offsets = drawing.coords_to_offsets(coords)
    offsets = offsets[:drawing.MAX_STROKE_LEN]
    offsets, normalizationFactor = drawing.normalize(offsets, returnNormalizationFactor=True)
    return offsets, normalizationFactor


def undo_preprocess(offsets, normalizationFactor):

    # TODO: normalization
    offsets[:, :2] *= normalizationFactor

    # Convert from relative to absolute positions
    coords = drawing.offsets_to_coords(offsets)

    # Convert to PenPosition
    results = [PenPosition(coord[0], -coord[1], coord[2], None, None, None) for coord in coords]

    return results


class GravesWriter(object):

    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        checkpoint_dir = os.path.join(dir_path,'..','checkpoints',"graves","iam_online")
        self.nn = rnn(
            log_dir='logs',
            # checkpoint_dir='/home/mayr/Documents/thesis_mstumpf/results/handwriting-synthesis/iam_online',
            checkpoint_dir=checkpoint_dir,
            prediction_dir=None,
            learning_rates=[.0001, .00005, .00002],
            batch_sizes=[32, 64, 64],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            validation_batch_size=32,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        self.nn.restore()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.nn.session.close()
        del self.nn

    def write(self, newText, oldText, oldStrokes, bias=0.9):

        # Sanity check
        valid_char_set = set(drawing.alphabet)
        for line_num, line in [('old-text', oldText), ('new-text', newText)]:
            if len(line) > 75:
                raise ValueError(
                    (
                        "Each line must be at most 75 characters. "
                        "Line {} contains {}"
                    ).format(line_num, len(line))
                )

            for char in line:
                if char not in valid_char_set:
                    raise ValueError(
                        (
                            "Invalid character {} detected in line {}. "
                            "Valid character set is {}"
                        ).format(char, line_num, valid_char_set)
                    )

        # Preprocess strokes
        preprocessedOldStrokes, normalizationFactor = preprocess(oldStrokes)

        # Run the actual neural network handwriting fake step
        generatedSamples = self._sample(newText, preprocessedOldStrokes, oldText, bias=bias)

        # Undo the preprocessing
        newStrokes = undo_preprocess(generatedSamples, normalizationFactor)

        return newStrokes

    # line = new_text
    # c_p = old_text
    def _sample(self, line, x_p, c_p, bias=None):

        max_tsteps = 40 * len(line)
        biases = [bias] if bias is not None else [0.5]

        x_prime = np.zeros([1, 2000, 3])
        x_prime_len = np.zeros([1])
        chars = np.zeros([1, 120])
        chars_len = np.zeros([1])

        c_p = c_p + " " + line
        c_p = drawing.encode_ascii(c_p)
        c_p = np.array(c_p)

        x_prime[0, :len(x_p), :] = x_p
        x_prime_len[0] = len(x_p)
        chars[0, :len(c_p)] = c_p
        chars_len[0] = len(c_p)

        feed_dict = {self.nn.prime: True,
            self.nn.x_prime: x_prime,
            self.nn.x_prime_len: x_prime_len,
            self.nn.num_samples: 1,
            self.nn.sample_tsteps: max_tsteps,
            self.nn.c: chars,
            self.nn.c_len: chars_len,
            self.nn.bias: biases}

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict=feed_dict
        )
        return samples[0]
        #samples = [sample[~np.all(sample == 0.0, axis=1)] for sample in samples]
        #return samples
