# coding=utf-8
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Input/output checkpointing."""

import os
import random
import sys
import numpy as np

import torch
from torch.nn.parallel import DistributedDataParallel as torchDDP

from megatron import mpu, get_args
from megatron import get_args
from megatron import print_rank_0

_CHECKPOINT_VERSION = None


def set_checkpoint_version(value):
    global _CHECKPOINT_VERSION
    assert _CHECKPOINT_VERSION is None, "checkpoint version already set"
    _CHECKPOINT_VERSION = value


def get_checkpoint_version():
    global _CHECKPOINT_VERSION
    return _CHECKPOINT_VERSION


def check_checkpoint_args(checkpoint_args):
    """Ensure fixed arguments for a model are the same for the input
    arguments and the one retreived frm checkpoint."""
    args = get_args()

    def _compare(arg_name):
        checkpoint_value = getattr(checkpoint_args, arg_name)
        args_value = getattr(args, arg_name)
        error_message = ("{} value from checkpoint ({}) is not equal to the "
                         "input argument value ({}).".format(
                             arg_name, checkpoint_value, args_value))
        assert checkpoint_value == args_value, error_message

    _compare("num_layers")
    _compare("hidden_size")
    _compare("num_attention_heads")
    _compare("max_position_embeddings")
    _compare("make_vocab_size_divisible_by")
    _compare("padded_vocab_size")
    _compare("tokenizer_type")
    _compare("model_parallel_size")


def ensure_directory_exists(filename):
    """Build filename's path if it does not already exists."""
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def get_checkpoint_name(checkpoints_path,
                        iteration,
                        release=False,
                        mp_rank=None):
    """A unified checkpoint name."""
    if release:
        directory = "release"
    else:
        directory = "iter_{:07d}".format(iteration)
    return os.path.join(
        checkpoints_path,
        directory,
        "mp_rank_{:02d}".format(
            mpu.get_model_parallel_rank() if mp_rank is None else mp_rank),
        "model_optim_rng.pt",
    )


def get_checkpoint_tracker_filename(checkpoints_path):
    """Tracker file rescords the latest chckpoint during
    training to restart from."""
    return os.path.join(checkpoints_path, "latest_checkpointed_iteration.txt")


def save_ds_checkpoint(iteration, model, args):
    """Save a model checkpoint."""

    sd = {}
    sd["iteration"] = iteration
    sd["checkpoint_version"] = 2.0
    sd["args"] = args

    # rng states.
    if not args.no_save_rng:
        sd["random_rng_state"] = random.getstate()
        sd["np_rng_state"] = np.random.get_state()
        sd["torch_rng_state"] = torch.get_rng_state()
        sd["cuda_rng_state"] = torch.cuda.get_rng_state()
        sd["rng_tracker_states"] = mpu.get_cuda_rng_tracker().get_states()

    # megatron model uses state_dict_for_save_checkpointing instead of the standard state_dict
    # state_dict is used by deepscale for module saving so it needs to point to the right function
    original_state_dict = model.module.state_dict
    model.module.state_dict = model.module.state_dict_for_save_checkpoint
    try:
        model.save_checkpoint(args.save, client_state=sd)
    finally:
        model.module.state_dict = original_state_dict


def save_checkpoint(iteration, model, optimizer, lr_scheduler):
    """Save a model checkpoint."""
    args = get_args()

    if args.deepscale:
        save_ds_checkpoint(iteration, model, args)
    else:
        # Only rank zero of the data parallel writes to the disk.
        if isinstance(model, torchDDP):
            model = model.module
        if mpu.get_data_parallel_rank() == 0:

            # Arguments, iteration, and model.
            state_dict = {}
            state_dict["args"] = args
            state_dict["checkpoint_version"] = 2.0
            state_dict["iteration"] = iteration
            state_dict["model"] = model.state_dict_for_save_checkpoint()

            # Optimizer stuff.
            if not args.no_save_optim:
                if optimizer is not None:
                    state_dict["optimizer"] = optimizer.state_dict()
                if lr_scheduler is not None:
                    state_dict["lr_scheduler"] = lr_scheduler.state_dict()

            # RNG states.
            if not args.no_save_rng:
                state_dict["random_rng_state"] = random.getstate()
                state_dict["np_rng_state"] = np.random.get_state()
                state_dict["torch_rng_state"] = torch.get_rng_state()
                state_dict["cuda_rng_state"] = torch.cuda.get_rng_state()
                state_dict["rng_tracker_states"] = (
                    mpu.get_cuda_rng_tracker().get_states())

            # Save.
            checkpoint_name = get_checkpoint_name(args.save, iteration)
            print(
                "global rank {} is saving checkpoint at iteration {:7d} to {}".
                format(torch.distributed.get_rank(), iteration,
                       checkpoint_name))
            ensure_directory_exists(checkpoint_name)
            torch.save(state_dict, checkpoint_name)
            print("  successfully saved {}".format(checkpoint_name))

    # Wait so everyone is done (necessary)
    torch.distributed.barrier()
    # And update the latest iteration
    if torch.distributed.get_rank() == 0:
        tracker_filename = get_checkpoint_tracker_filename(args.save)
        with open(tracker_filename, "w") as f:
            f.write(str(iteration))
    # Wait so everyone is done (not necessary)
    torch.distributed.barrier()


def load_checkpoint(model, optimizer, lr_scheduler, load_arg="load"):
    """Load a model checkpoint and return the iteration."""
    args = get_args()
    load_dir = getattr(args, load_arg)

    if isinstance(model, torchDDP):
        model = model.module
    # Read the tracker file and set the iteration.
    tracker_filename = get_checkpoint_tracker_filename(load_dir)

    # If no tracker file, return iretation zero.
    if not os.path.isfile(tracker_filename):
        print_rank_0("WARNING: could not find the metadata file {} ".format(
            tracker_filename))
        print_rank_0("    will not load any checkpoints and will start from "
                     "random")
        return 0

    # Otherwise, read the tracker file and either set the iteration or
    # mark it as a release checkpoint.
    iteration = 0
    release = False
    with open(tracker_filename, "r") as f:
        metastring = f.read().strip()
        try:
            iteration = int(metastring)
        except ValueError:
            release = metastring == "release"
            if not release:
                print_rank_0("ERROR: Invalid metadata file {}. Exiting".format(
                    tracker_filename))
                sys.exit()

    assert iteration > 0 or release, "error parsing metadata file {}".format(
        tracker_filename)

    if args.deepscale:
        checkpoint_name, state_dict = model.load_checkpoint(load_dir)

        if checkpoint_name is None:
            if mpu.get_data_parallel_rank() == 0:
                print("Unable to load checkpoint.")
            return iteration

    else:
        # Checkpoint.
        checkpoint_name = get_checkpoint_name(load_dir, iteration, release)
        if mpu.get_data_parallel_rank() == 0:
            print("global rank {} is loading checkpoint {}".format(
                torch.distributed.get_rank(), checkpoint_name))

        # Load the checkpoint.
        try:
            state_dict = torch.load(checkpoint_name, map_location="cpu")
        except ModuleNotFoundError:
            # For backward compatibility.
            print_rank_0(" > deserializing using the old code structure ...")
            sys.modules["fp16.loss_scaler"] = sys.modules[
                "megatron.fp16.loss_scaler"]
            state_dict = torch.load(checkpoint_name, map_location="cpu")
            sys.modules.pop("fp16.loss_scaler", None)
        except BaseException:
            print_rank_0("could not load the checkpoint")
            sys.exit()
            # Model.

        model.load_state_dict(state_dict["model"])

        # Optimizer.
        if not release and not args.finetune and not args.no_load_optim:
            try:
                if optimizer is not None:
                    optimizer.load_state_dict(state_dict["optimizer"])
                if lr_scheduler is not None:
                    lr_scheduler.load_state_dict(state_dict["lr_scheduler"])
            except KeyError:
                print_rank_0(
                    "Unable to load optimizer from checkpoint {}. "
                    "Specify --no-load-optim or --finetune to prevent "
                    "attempting to load the optimizer state, "
                    "exiting ...".format(checkpoint_name))
                sys.exit()

    # set checkpoint version
    set_checkpoint_version(state_dict.get("checkpoint_version", 0))

    # Set iteration.
    if args.finetune or release:
        iteration = 0
    else:
        try:
            iteration = state_dict["iteration"]
        except KeyError:
            try:  # Backward compatible with older checkpoints
                iteration = state_dict["total_iters"]
            except KeyError:
                print_rank_0("A metadata file exists but unable to load "
                             "iteration from checkpoint {}, exiting".format(
                                 checkpoint_name))
                sys.exit()

    # Check arguments.
    if "args" in state_dict:
        checkpoint_args = state_dict["args"]
        check_checkpoint_args(checkpoint_args)
    else:
        print_rank_0("could not find arguments in the checkpoint ...")

    # rng states.
    if not release and not args.finetune and not args.no_load_rng:
        try:
            random.setstate(state_dict["random_rng_state"])
            np.random.set_state(state_dict["np_rng_state"])
            torch.set_rng_state(state_dict["torch_rng_state"])
            torch.cuda.set_rng_state(state_dict["cuda_rng_state"])
            mpu.get_cuda_rng_tracker().set_states(
                state_dict["rng_tracker_states"])
        except KeyError:
            print_rank_0("Unable to load optimizer from checkpoint {}. "
                         "Specify --no-load-rng or --finetune to prevent "
                         "attempting to load the optimizer state, "
                         "exiting ...".format(checkpoint_name))
            sys.exit()

    torch.distributed.barrier()
    if mpu.get_data_parallel_rank() == 0:
        print("  successfully loaded {}".format(checkpoint_name))

    return iteration


def load_ict_checkpoint(model,
                        only_query_model=False,
                        only_block_model=False,
                        from_realm_chkpt=False):
    """selectively load ICT models for indexing/retrieving from ICT or REALM checkpoints"""

    args = get_args()

    if isinstance(model, torchDDP):
        model = model.module

    load_path = args.load if from_realm_chkpt else args.ict_load

    tracker_filename = get_checkpoint_tracker_filename(load_path)
    with open(tracker_filename, "r") as f:
        iteration = int(f.read().strip())

    # assert iteration > 0
    checkpoint_name = get_checkpoint_name(load_path, iteration, False)
    if mpu.get_data_parallel_rank() == 0:
        print("global rank {} is loading checkpoint {}".format(
            torch.distributed.get_rank(), checkpoint_name))

    state_dict = torch.load(checkpoint_name, map_location="cpu")
    ict_state_dict = state_dict["model"]
    if from_realm_chkpt and mpu.get_data_parallel_rank() == 0:
        print(" loading ICT state dict from REALM", flush=True)
        ict_state_dict = ict_state_dict["retriever"]["ict_model"]

    if only_query_model:
        ict_state_dict.pop("context_model")
    if only_block_model:
        ict_state_dict.pop("question_model")

    model.load_state_dict(ict_state_dict)
    torch.distributed.barrier()

    if mpu.get_data_parallel_rank() == 0:
        print(" successfully loaded {}".format(checkpoint_name))

    return model
