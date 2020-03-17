#!/bin/bash

. ~/work/thesis-venv/bin/activate

python --version

timestamp=`date +%s`

#CP_DIR=/home/martin/work/thesis/ext/pix2pix/checkpoints
#NET_NAME=1565600196_cond_pix2pix_256_colored_retry

CP_DIR=/home/martin/work/thesis/ext/pix2pix/checkpoints
NET_NAME=test

DATA_DIR=/home/martin/work/thesis/ext/datasets/cvl/background_test/joined_pix2pix


python test.py --dataroot $DATA_DIR \
               --name $NET_NAME \
               --checkpoints_dir $CP_DIR \
               --model cond_pix2pix \
               --phase train \
               --batch_size 16 \
               --preprocess none \
               --num_test 100000000 \
               --no_dropout
                

#/home/martin/cluster/thesis/ext/pix2pix/datasets/test  \
#                \
               #--input_nc 3 \
#                --load_size 140 \
#                --crop_size 128
