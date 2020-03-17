#!/usr/bin/env python3

from __future__ import print_function
from xml.etree import ElementTree

import numpy as np

import drawing
import operator

import argparse
import os
import sys

from tqdm import tqdm

def get_stroke_sequence(sampleStrokes):

    strokes = sampleStrokes

    coords = []
    if strokes[0][2] < 0.5:
        coords = [[0,0,1]]

    for i, point in enumerate(strokes):
        coords.append([
            int(point[0]),
            -1*int(point[1]),
            point[2]
        ])
    coords = np.array(coords)

    coords = drawing.align(coords)
    coords = drawing.denoise(coords)
    offsets = drawing.coords_to_offsets(coords)
    offsets = offsets[:drawing.MAX_STROKE_LEN]
    offsets = drawing.normalize(offsets)
    return offsets


def get_ascii_sequences(filename):
    sequences = open(filename, 'r').read()
    sequences = sequences.replace(r'%%%%%%%%%%%', '\n')
    sequences = [i.strip() for i in sequences.split('\n')]
    lines = sequences[sequences.index('CSR:') + 2:]
    lines = [line.strip() for line in lines if line.strip()]
    lines = [drawing.encode_ascii(line)[:drawing.MAX_CHAR_LEN] for line in lines]
    return lines


def int_labels_to_text(line_int, eoc_labels, bow_labels, dataset):
    assert(len(line_int) == len(bow_labels))
    assert(len(line_int) == len(eoc_labels))

    result = ""
    
    charHist = dict()
    for char_label, eoc_label, bow_label in zip(line_int, eoc_labels, bow_labels):

        if bow_label > 0.5:
            result += " "

        if char_label not in charHist:
            charHist[char_label] = 1
        else:
            charHist[char_label] += 1

        if eoc_label:
            maxCharInt = max(charHist.items(), key=operator.itemgetter(1))[0]
            maxChar = dataset.char_encoder.inverse_transform([maxCharInt])[0]
            result += maxChar
            #print(maxChar)
            charHist = dict()
    return result 



def collect_data(fnames):
#    fnames = []
#    for dirpath, dirnames, filenames in os.walk('data/raw_npz/'):
#        if dirnames:
#            continue
#        for filename in filenames:
#            if filename.startswith('.'):
#                continue
#            if not filename.endswith('.npz'):
#                continue
#            print(os.path.join(dirpath,filename))
#            fnames.append(os.path.join(dirpath, filename))
    
    
    x_out = []
    c_out = []

    for i, fname in enumerate(fnames):
        print('loading \'' + fname + '\'...')  
        dataset = np.load(fname, allow_pickle=True)

        assert(len(dataset['samples']) == len(dataset['texts']))
        for strokes, text in zip(tqdm(dataset['samples'], file=sys.stdout), dataset['texts']):
            x_out.append(strokes)
            c_out.append(drawing.encode_ascii(text.strip())[:drawing.MAX_CHAR_LEN])

    return x_out, c_out


if __name__ == '__main__':
 
    parser = argparse.ArgumentParser(description='Converts npz files to actual training libraries')
    parser.add_argument('npz_files', nargs='+', help='The input npz files.')
    parser.add_argument('output', help='The output folder where to store the resulting dataset.')
    args = parser.parse_args()
    print(args)

    print('loading data...')
    input_x, input_c = collect_data(args.npz_files)
    #print(len(input_x), len(input_c))

    print('dumping to numpy arrays...')
    x = np.zeros([len(input_x), drawing.MAX_STROKE_LEN, 3], dtype=np.float32)
    x_len = np.zeros([len(input_x)], dtype=np.int16)
    c = np.zeros([len(input_x), drawing.MAX_CHAR_LEN], dtype=np.int8)
    c_len = np.zeros([len(input_x)], dtype=np.int8)
    valid_mask = np.zeros([len(input_x)], dtype=np.bool)

    for i, (x_i_raw, c_i) in enumerate(zip(tqdm(input_x, file=sys.stdout), input_c)):

        #if i % 200 == 0:
        #    print(i, '\t', '/', len(input_x))

        x_i = get_stroke_sequence(x_i_raw)
        valid_mask[i] = ~np.any(np.linalg.norm(x_i[:, :2], axis=1) > 60)

        x[i, :len(x_i), :] = x_i
        x_len[i] = len(x_i)

        c[i, :len(c_i)] = c_i
        c_len[i] = len(c_i)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    np.save(os.path.join(args.output,'x.npy'), x[valid_mask])
    np.save(os.path.join(args.output,'x_len.npy'), x_len[valid_mask])
    np.save(os.path.join(args.output,'c.npy'), c[valid_mask])
    np.save(os.path.join(args.output,'c_len.npy'), c_len[valid_mask])
