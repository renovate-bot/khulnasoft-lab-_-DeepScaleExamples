#!/bin/bash

# If you are able to install pytorch >= 1.8
# (and nccl >= 2.8.3 if you have 64 or more GPUs),
# we highly recommend you to use the NCCL-based 1-bit Adam
# which has better performance and ease of use
# (see scripts in DeepScaleExamples/bing_bert/1-bit_adam/nccl
# and read the tutorial for more details:
# https://www.deepscale.khulnasoft.com/tutorials/onebit-adam/)

base_dir=`pwd`

# Where should we save checkpoints and tensorboard events?
JOB_NAME=onebit_adam_4k_seq128_mpi_infiniband
OUTPUT_DIR=${base_dir}/bert_model_outputs

mkdir -p $OUTPUT_DIR

NCCL_TREE_THRESHOLD=0 deepscale --launcher=mvapich ${base_dir}/../../deepscale_train.py \
--cf ${base_dir}/../../bert_large.json \
--max_seq_length 128 \
--output_dir $OUTPUT_DIR \
--deepscale_mpi \
--deepscale \
--deepscale_transformer_kernel \
--print_steps 40 \
--lr_schedule "LE" \
--lr_offset 0.0 \
--job_name $JOB_NAME \
--deepscale_config ${base_dir}/deepscale_bsz4k_onebitadam_config_seq128_mpi_infiniband.json \
--data_path_prefix /data/bert \
&> ${JOB_NAME}.log
