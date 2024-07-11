#!/bin/bash

# If you are able to install pytorch >= 1.8
# (and nccl >= 2.8.3 if you have 64 or more GPUs),
# we highly recommend you to use the NCCL-based 1-bit Lamb
# which has better performance and ease of use
# (see scripts in DeepScaleExamples/bing_bert/1-bit_lamb/nccl
# and read the tutorial for more details:
# https://www.deepscale.khulnasoft.com/tutorials/onebit-lamb/)

# Note: Please use the deepscale launch script for most cases.
# For advanced users, mpirun or other MPI launchers can be used
# with this script as follows.
# mpirun -n 2 [launcher-args] python ${base_dir}/../deepscale_train.py
# As an example, below we include the command we used

base_dir=`pwd`

# Assumes job name in previous seq128 run, will resume training from epoch 150
EPOCH=150

# Where should we save checkpoints and tensorboard events?
JOB_NAME=onebit_lamb_32k_chkpt${EPOCH}_seq512_mpirun_ethernet
OUTPUT_DIR=${base_dir}/bert_model_outputs

CHECKPOINT_BASE_PATH=${OUTPUT_DIR}/saved_models/onebit_lamb_64k_seq128_mpirun_ethernet
CHECKPOINT_NAME=`basename ${CHECKPOINT_BASE_PATH}/epoch${EPOCH}_*`
echo "checkpoint id: $CHECKPOINT_NAME"

mkdir -p $OUTPUT_DIR

# NCCL_IB_DISABLE=1 NCCL_SOCKET_IFNAME=eth0 are used to disable infiniband. Remove it if needed.
mpirun -n 128 -npernode 4 -hostfile /job/hostfile -x UCX_TLS=tcp --mca btl ^openib --mca btl_tcp_if_include eth0 -x NCCL_TREE_THRESHOLD=0 -x NCCL_IB_DISABLE=1 -x NCCL_SOCKET_IFNAME=eth0 python ${base_dir}/../../deepscale_train.py \
--cf ${base_dir}/../../bert_large_lamb.json \
--max_seq_length 512 \
--output_dir $OUTPUT_DIR \
--print_steps 100 \
--deepscale_mpi \
--deepscale \
--deepscale_transformer_kernel \
--job_name $JOB_NAME \
--deepscale_config ${base_dir}/deepscale_bsz32k_onebitlamb_config_seq512_mpi_ethernet.json \
--data_path_prefix /data/bert \
--validation_data_path_prefix /data/bert \
--rewarmup \
--lr_schedule "EE" \
--attention_dropout_checkpoint \
--lr_offset 0.0 \
--load_training_checkpoint ${CHECKPOINT_BASE_PATH} \
--load_checkpoint_id ${CHECKPOINT_NAME} \
&> ${JOB_NAME}.log
