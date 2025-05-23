..
    Copyright 2020 The HuggingFace Team. All rights reserved.

    Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
    an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
    specific language governing permissions and limitations under the License.

Trainer
-----------------------------------------------------------------------------------------------------------------------

The :class:`~transformers.Trainer` and :class:`~transformers.TFTrainer` classes provide an API for feature-complete
training in most standard use cases. It's used in most of the :doc:`example scripts <../examples>`.

Before instantiating your :class:`~transformers.Trainer`/:class:`~transformers.TFTrainer`, create a
:class:`~transformers.TrainingArguments`/:class:`~transformers.TFTrainingArguments` to access all the points of
customization during training.

The API supports distributed training on multiple GPUs/TPUs, mixed precision through `NVIDIA Apex
<https://github.com/NVIDIA/apex>`__ for PyTorch and :obj:`tf.keras.mixed_precision` for TensorFlow.

Both :class:`~transformers.Trainer` and :class:`~transformers.TFTrainer` contain the basic training loop supporting the
previous features. To inject custom behavior you can subclass them and override the following methods:

- **get_train_dataloader**/**get_train_tfdataset** -- Creates the training DataLoader (PyTorch) or TF Dataset.
- **get_eval_dataloader**/**get_eval_tfdataset** -- Creates the evaluation DataLoader (PyTorch) or TF Dataset.
- **get_test_dataloader**/**get_test_tfdataset** -- Creates the test DataLoader (PyTorch) or TF Dataset.
- **log** -- Logs information on the various objects watching training.
- **create_optimizer_and_scheduler** -- Setups the optimizer and learning rate scheduler if they were not passed at
  init.
- **compute_loss** - Computes the loss on a batch of training inputs.
- **training_step** -- Performs a training step.
- **prediction_step** -- Performs an evaluation/test step.
- **run_model** (TensorFlow only) -- Basic pass through the model.
- **evaluate** -- Runs an evaluation loop and returns metrics.
- **predict** -- Returns predictions (with metrics if labels are available) on a test set.

Here is an example of how to customize :class:`~transformers.Trainer` using a custom loss function:

.. code-block:: python

    from transformers import Trainer
    class MyTrainer(Trainer):
        def compute_loss(self, model, inputs):
            labels = inputs.pop("labels")
            outputs = model(**inputs)
            logits = outputs[0]
            return my_custom_loss(logits, labels)

Another way to customize the training loop behavior for the PyTorch :class:`~transformers.Trainer` is to use
:doc:`callbacks <callback>` that can inspect the training loop state (for progress reporting, logging on TensorBoard or
other ML platforms...) and take decisions (like early stopping).


Trainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.Trainer
    :members:


Seq2SeqTrainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.Seq2SeqTrainer
    :members: evaluate, predict


TFTrainer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.TFTrainer
    :members:


TrainingArguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.TrainingArguments
    :members:


Seq2SeqTrainingArguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.Seq2SeqTrainingArguments
    :members:


TFTrainingArguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: transformers.TFTrainingArguments
    :members:


Trainer Integrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



The :class:`~transformers.Trainer` has been extended to support libraries that may dramatically improve your training
time and fit much bigger models.

Currently it supports third party solutions, `DeepScale <https://github.com/khulnasoft/DeepScale>`__ and `FairScale
<https://github.com/facebookresearch/fairscale/>`__, which implement parts of the paper `ZeRO: Memory Optimizations
Toward Training Trillion Parameter Models, by Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, Yuxiong He
<https://arxiv.org/abs/1910.02054>`__.

This provided support is new and experimental as of this writing.

Installation Notes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As of this writing, both FairScale and Deepscale require compilation of CUDA C++ code, before they can be used.

While all installation issues should be dealt with through the corresponding GitHub Issues of `FairScale
<https://github.com/facebookresearch/fairscale/issues>`__ and `Deepscale
<https://github.com/khulnasoft/DeepScale/issues>`__, there are a few common issues that one may encounter while building
any PyTorch extension that needs to build CUDA extensions.

Therefore, if you encounter a CUDA-related build issue while doing one of the following or both:

.. code-block:: bash

    pip install fairscale
    pip install deepscale

please, read the following notes first.

In these notes we give examples for what to do when ``pytorch`` has been built with CUDA ``10.2``. If your situation is
different remember to adjust the version number to the one you are after.

**Possible problem #1:**

While, Pytorch comes with its own CUDA toolkit, to build these two projects you must have an identical version of CUDA
installed system-wide.

For example, if you installed ``pytorch`` with ``cudatoolkit==10.2`` in the Python environment, you also need to have
CUDA ``10.2`` installed system-wide.

The exact location may vary from system to system, but ``/usr/local/cuda-10.2`` is the most common location on many
Unix systems. When CUDA is correctly set up and added to the ``PATH`` environment variable, one can find the
installation location by doing:

.. code-block:: bash

    which nvcc

If you don't have CUDA installed system-wide, install it first. You will find the instructions by using your favorite
search engine. For example, if you're on Ubuntu you may want to search for: `ubuntu cuda 10.2 install
<https://www.google.com/search?q=ubuntu+cuda+10.2+install>`__.

**Possible problem #2:**

Another possible common problem is that you may have more than one CUDA toolkit installed system-wide. For example you
may have:

.. code-block:: bash

    /usr/local/cuda-10.2
    /usr/local/cuda-11.0

Now, in this situation you need to make sure that your ``PATH`` and ``LD_LIBRARY_PATH`` environment variables contain
the correct paths to the desired CUDA version. Typically, package installers will set these to contain whatever the
last version was installed. If you encounter the problem, where the package build fails because it can't find the right
CUDA version despite you having it installed system-wide, it means that you need to adjust the 2 aforementioned
environment variables.

First, you may look at their contents:

.. code-block:: bash

    echo $PATH
    echo $LD_LIBRARY_PATH

so you get an idea of what is inside.

It's possible that ``LD_LIBRARY_PATH`` is empty.

``PATH`` lists the locations of where executables can be found and ``LD_LIBRARY_PATH`` is for where shared libraries
are to looked for. In both cases, earlier entries have priority over the later ones. ``:`` is used to separate multiple
entries.

Now, to tell the build program where to find the specific CUDA toolkit, insert the desired paths to be listed first by
doing:

.. code-block:: bash

    export PATH=/usr/local/cuda-10.2/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH

Note that we aren't overwriting the existing values, but prepending instead.

Of course, adjust the version number, the full path if need be. Check that the directories you assign actually do
exist. ``lib64`` sub-directory is where the various CUDA ``.so`` objects, like ``libcudart.so`` reside, it's unlikely
that your system will have it named differently, but if it is adjust it to reflect your reality.


**Possible problem #3:**

Some older CUDA versions may refuse to build with newer compilers. For example, you my have ``gcc-9`` but it wants
``gcc-7``.

There are various ways to go about it.

If you can install the latest CUDA toolkit it typically should support the newer compiler.

Alternatively, you could install the lower version of the compiler in addition to the one you already have, or you may
already have it but it's not the default one, so the build system can't see it. If you have ``gcc-7`` installed but the
build system complains it can't find it, the following might do the trick:

.. code-block:: bash

    sudo ln -s /usr/bin/gcc-7  /usr/local/cuda-10.2/bin/gcc
    sudo ln -s /usr/bin/g++-7  /usr/local/cuda-10.2/bin/g++


Here, we are making a symlink to ``gcc-7`` from ``/usr/local/cuda-10.2/bin/gcc`` and since
``/usr/local/cuda-10.2/bin/`` should be in the ``PATH`` environment variable (see the previous problem's solution), it
should find ``gcc-7`` (and ``g++7``) and then the build will succeed.

As always make sure to edit the paths in the example to match your situation.

**If still unsuccessful:**

If after addressing these you still encounter build issues, please, proceed with the GitHub Issue of `FairScale
<https://github.com/facebookresearch/fairscale/issues>`__ and `Deepscale
<https://github.com/khulnasoft/DeepScale/issues>`__, depending on the project you have the problem with.


FairScale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By integrating `FairScale <https://github.com/facebookresearch/fairscale/>`__ the :class:`~transformers.Trainer`
provides support for the following features from `the ZeRO paper <https://arxiv.org/abs/1910.02054>`__:

1. Optimizer State Sharding
2. Gradient Sharding

You will need at least two GPUs to use this feature.

To deploy this feature:

1. Install the library via pypi:

   .. code-block:: bash

       pip install fairscale

   or find more details on `the FairScale's GitHub page
   <https://github.com/facebookresearch/fairscale/#installation>`__.

2. Add ``--sharded_ddp`` to the command line arguments, and make sure you have added the distributed launcher ``-m
   torch.distributed.launch --nproc_per_node=NUMBER_OF_GPUS_YOU_HAVE`` if you haven't been using it already.

For example here is how you could use it for ``run_seq2seq.py`` with 2 GPUs:

.. code-block:: bash

    python -m torch.distributed.launch --nproc_per_node=2 examples/seq2seq/run_seq2seq.py \
    --model_name_or_path t5-small --per_device_train_batch_size 1   \
    --output_dir output_dir --overwrite_output_dir \
    --do_train --max_train_samples 500 --num_train_epochs 1 \
    --dataset_name wmt16 --dataset_config "ro-en" \
    --task translation_en_to_ro --source_prefix "translate English to Romanian: " \
    --fp16 --sharded_ddp

Notes:

- This feature requires distributed training (so multiple GPUs).
- It is not implemented for TPUs.
- It works with ``--fp16`` too, to make things even faster.
- One of the main benefits of enabling ``--sharded_ddp`` is that it uses a lot less GPU memory, so you should be able
  to use significantly larger batch sizes using the same hardware (e.g. 3x and even bigger) which should lead to
  significantly shorter training time.


DeepScale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`DeepScale <https://github.com/khulnasoft/DeepScale>`__ implements everything described in the `ZeRO paper
<https://arxiv.org/abs/1910.02054>`__, except ZeRO's stage 3. "Parameter Partitioning (Pos+g+p)". Currently it provides
full support for:

1. Optimizer State Partitioning (ZeRO stage 1)
2. Add Gradient Partitioning (ZeRO stage 2)
3. Custom fp16 handling
4. A range of fast Cuda-extension-based Optimizers
5. ZeRO-Offload

ZeRO-Offload has its own dedicated paper: `ZeRO-Offload: Democratizing Billion-Scale Model Training
<https://arxiv.org/abs/2101.06840>`__.

DeepScale is currently used only for training, as all the currently available features are of no use to inference.



Installation
=======================================================================================================================

Install the library via pypi:

.. code-block:: bash

    pip install deepscale

or find more details on `the DeepScale's GitHub page <https://github.com/khulnasoft/deepscale#installation>`__.

Deployment with multiple GPUs
=======================================================================================================================

To deploy this feature with multiple GPUs adjust the :class:`~transformers.Trainer` command line arguments as
following:

1. replace ``python -m torch.distributed.launch`` with ``deepscale``.
2. add a new argument ``--deepscale ds_config.json``, where ``ds_config.json`` is the DeepScale configuration file as
   documented `here <https://www.deepscale.khulnasoft.com/docs/config-json/>`__. The file naming is up to you.

Therefore, if your original command line looked as following:

.. code-block:: bash

    python -m torch.distributed.launch --nproc_per_node=2 your_program.py <normal cl args>

Now it should be:

.. code-block:: bash

    deepscale --num_gpus=2 your_program.py <normal cl args> --deepscale ds_config.json

Unlike, ``torch.distributed.launch`` where you have to specify how many GPUs to use with ``--nproc_per_node``, with the
``deepscale`` launcher you don't have to use the corresponding ``--num_gpus`` if you want all of your GPUs used. The
full details on how to configure various nodes and GPUs can be found `here
<https://www.deepscale.khulnasoft.com/getting-started/#resource-configuration-multi-node>`__.

In fact, you can continue using ``-m torch.distributed.launch`` with DeepScale as long as you don't need to use
``deepscale`` launcher-specific arguments. Typically if you don't need a multi-node setup you're not required to use
the ``deepscale`` launcher. But since in the DeepScale documentation it'll be used everywhere, for consistency we will
use it here as well.

Here is an example of running ``run_seq2seq.py`` under DeepScale deploying all available GPUs:

.. code-block:: bash

    deepscale examples/seq2seq/run_seq2seq.py \
    --deepscale examples/tests/deepscale/ds_config.json \
    --model_name_or_path t5-small --per_device_train_batch_size 1   \
    --output_dir output_dir --overwrite_output_dir --fp16 \
    --do_train --max_train_samples 500 --num_train_epochs 1 \
    --dataset_name wmt16 --dataset_config "ro-en" \
    --task translation_en_to_ro --source_prefix "translate English to Romanian: "


Note that in the DeepScale documentation you are likely to see ``--deepscale --deepscale_config ds_config.json`` - i.e.
two DeepScale-related arguments, but for the sake of simplicity, and since there are already so many arguments to deal
with, we combined the two into a single argument.

For some practical usage examples, please, see this `post
<https://github.com/huggingface/transformers/issues/8771#issuecomment-759248400>`__.



Deployment with one GPU
=======================================================================================================================

To deploy DeepScale with one GPU adjust the :class:`~transformers.Trainer` command line arguments as following:

.. code-block:: bash

    deepscale --num_gpus=1 examples/seq2seq/run_seq2seq.py \
    --deepscale examples/tests/deepscale/ds_config.json \
    --model_name_or_path t5-small --per_device_train_batch_size 1   \
    --output_dir output_dir --overwrite_output_dir --fp16 \
    --do_train --max_train_samples 500 --num_train_epochs 1 \
    --dataset_name wmt16 --dataset_config "ro-en" \
    --task translation_en_to_ro --source_prefix "translate English to Romanian: "

This is almost the same as with multiple-GPUs, but here we tell DeepScale explicitly to use just one GPU. By default,
DeepScale deploys all GPUs it can see. If you have only 1 GPU to start with, then you don't need this argument. The
following `documentation <https://www.deepscale.khulnasoft.com/getting-started/#resource-configuration-multi-node>`__ discusses the
launcher options.

Why would you want to use DeepScale with just one GPU?

1. It has a ZeRO-offload feature which can delegate some computations and memory to the host's CPU and RAM, and thus
   leave more GPU resources for model's needs - e.g. larger batch size, or enabling a fitting of a very big model which
   normally won't fit.
2. It provides a smart GPU memory management system, that minimizes memory fragmentation, which again allows you to fit
   bigger models and data batches.

While we are going to discuss the configuration in details next, the key to getting a huge improvement on a single GPU
with DeepScale is to have at least the following configuration in the configuration file:

.. code-block:: json

  {
    "zero_optimization": {
       "stage": 2,
       "allgather_partitions": true,
       "allgather_bucket_size": 2e8,
       "reduce_scatter": true,
       "reduce_bucket_size": 2e8,
       "overlap_comm": true,
       "contiguous_gradients": true,
       "cpu_offload": true
    },
  }

which enables ``cpu_offload`` and some other important features. You may experiment with the buffer sizes, you will
find more details in the discussion below.

For a practical usage example of this type of deployment, please, see this `post
<https://github.com/huggingface/transformers/issues/8771#issuecomment-759176685>`__.

Notes:

- if you need to run on a specific GPU, which is different from GPU 0, you can't use ``CUDA_VISIBLE_DEVICES`` to limit
  the visible scope of available GPUs. Instead, you have to use the following syntax:

   .. code-block:: bash

       deepscale --include localhost:1 examples/seq2seq/run_seq2seq.py ...

   In this example, we tell DeepScale to use GPU 1 (second gpu).



Deployment in Notebooks
=======================================================================================================================

The problem with running notebook cells as a script is that there is no normal ``deepscale`` launcher to rely on, so
under certain setups we have to emulate it.

Here is how you'd have to adjust your training code in the notebook to use DeepScale.

.. code-block:: python

    # DeepScale requires a distributed environment even when only one process is used.
    # This emulates a launcher in the notebook
    import os
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '9994' # modify if RuntimeError: Address already in use
    os.environ['RANK'] = "0"
    os.environ['LOCAL_RANK'] = "0"
    os.environ['WORLD_SIZE'] = "1"

    # Now proceed as normal, plus pass the deepscale config file
    training_args = TrainingArguments(..., deepscale="ds_config.json")
    trainer = Trainer(...)
    trainer.train()

Note: `...` stands for the normal arguments that you'd pass to the functions.

If you want to create the config file on the fly in the notebook in the current directory, you could have a dedicated
cell with:

.. code-block:: python

    %%bash
    cat <<'EOT' > ds_config.json
    {
        "fp16": {
            "enabled": true,
            "loss_scale": 0,
            "loss_scale_window": 1000,
            "hysteresis": 2,
            "min_loss_scale": 1
        },

        "zero_optimization": {
            "stage": 2,
            "allgather_partitions": true,
            "allgather_bucket_size": 2e8,
            "overlap_comm": true,
            "reduce_scatter": true,
            "reduce_bucket_size": 2e8,
            "contiguous_gradients": true,
            "cpu_offload": true
        },

        "zero_allow_untested_optimizer": true,

        "optimizer": {
            "type": "AdamW",
            "params": {
                "lr": 3e-5,
                "betas": [0.8, 0.999],
                "eps": 1e-8,
                "weight_decay": 3e-7
            }
        },

        "scheduler": {
            "type": "WarmupLR",
            "params": {
                "warmup_min_lr": 0,
                "warmup_max_lr": 3e-5,
                "warmup_num_steps": 500
            }
        },

        "steps_per_print": 2000,
        "wall_clock_breakdown": false
    }
    EOT


That's said if the script is not in the notebook cells, you can launch ``deepscale`` normally via shell from a cell
with:

.. code-block::

   !deepscale examples/seq2seq/run_seq2seq.py ...

or with bash magic, where you can write a multi-line code for the shell to run:

.. code-block::

   %%bash

   cd /somewhere
   deepscale examples/seq2seq/run_seq2seq.py ...




Configuration
=======================================================================================================================

For the complete guide to the DeepScale configuration options that can be used in its configuration file please refer
to the `following documentation <https://www.deepscale.khulnasoft.com/docs/config-json/>`__.

You can find dozens of DeepScale configuration examples that address various practical needs in `the DeepScaleExamples
repo <https://github.com/khulnasoft/DeepScaleExamples>`__:

.. code-block:: bash

  git clone https://github.com/khulnasoft/DeepScaleExamples
  cd DeepScaleExamples
  find . -name '*json'

Continuing the code from above, let's say you're looking to configure the Lamb optimizer. So you can search through the
example ``.json`` files with:

.. code-block:: bash

  grep -i Lamb $(find . -name '*json')

Some more examples are to be found in the `main repo <https://github.com/khulnasoft/DeepScale>`__ as well.

While you always have to supply the DeepScale configuration file, you can configure the DeepScale integration in
several ways:

1. Supply most of the configuration inside the file, and just use a few required command line arguments. This is the
   recommended way as it puts most of the configuration params in one place.
2. Supply just the ZeRO configuration params inside the file, and configure the rest using the normal
   :class:`~transformers.Trainer` command line arguments.
3. Any variation of the first two ways.

To get an idea of what DeepScale configuration file looks like, here is one that activates ZeRO stage 2 features,
enables FP16, uses AdamW optimizer and WarmupLR scheduler:

.. code-block:: json

    {
        "fp16": {
            "enabled": true,
            "loss_scale": 0,
            "loss_scale_window": 1000,
            "hysteresis": 2,
            "min_loss_scale": 1
        },

       "zero_optimization": {
           "stage": 2,
           "allgather_partitions": true,
           "allgather_bucket_size": 5e8,
           "overlap_comm": true,
           "reduce_scatter": true,
           "reduce_bucket_size": 5e8,
           "contiguous_gradients": true,
           "cpu_offload": true
       },

       "optimizer": {
         "type": "AdamW",
         "params": {
           "lr": 3e-5,
           "betas": [ 0.8, 0.999 ],
           "eps": 1e-8,
           "weight_decay": 3e-7
         }
       },
       "zero_allow_untested_optimizer": true,

       "scheduler": {
         "type": "WarmupLR",
         "params": {
           "warmup_min_lr": 0,
           "warmup_max_lr": 3e-5,
           "warmup_num_steps": 500
         }
       }
    }

If you already have a command line that you have been using with :class:`transformers.Trainer` args, you can continue
using those and the :class:`~transformers.Trainer` will automatically convert them into the corresponding DeepScale
configuration at run time. For example, you could use the following configuration file:

.. code-block:: json

    {
       "zero_optimization": {
           "stage": 2,
           "allgather_partitions": true,
           "allgather_bucket_size": 5e8,
           "overlap_comm": true,
           "reduce_scatter": true,
           "reduce_bucket_size": 5e8,
           "contiguous_gradients": true,
           "cpu_offload": true
       }
    }

and the following command line arguments:

.. code-block:: bash

    --learning_rate 3e-5 --warmup_steps 500 --adam_beta1 0.8 --adam_beta2 0.999 --adam_epsilon 1e-8 \
    --weight_decay 3e-7 --lr_scheduler_type constant_with_warmup --fp16 --fp16_backend amp

to achieve the same configuration as provided by the longer json file in the first example.

When you execute the program, DeepScale will log the configuration it received from the :class:`~transformers.Trainer`
to the console, so you can see exactly what the final configuration was passed to it.

Shared Configuration
=======================================================================================================================

Some configuration information is required by both the :class:`~transformers.Trainer` and DeepScale to function
correctly, therefore, to prevent conflicting definitions, which could lead to hard to detect errors, we chose to
configure those via the :class:`~transformers.Trainer` command line arguments.

Therefore, the following DeepScale configuration params shouldn't be used with the :class:`~transformers.Trainer`:

* ``train_batch_size``
* ``train_micro_batch_size_per_gpu``
* ``gradient_accumulation_steps``

as these will be automatically derived from the run time environment and the following 2 command line arguments:

.. code-block:: bash

    --per_device_train_batch_size 8 --gradient_accumulation_steps 2

which are always required to be supplied.

Of course, you will need to adjust the values in this example to your situation.



ZeRO
=======================================================================================================================

The ``zero_optimization`` section of the configuration file is the most important part (`docs
<https://www.deepscale.khulnasoft.com/docs/config-json/#zero-optimizations-for-fp16-training>`__), since that is where you define
which ZeRO stages you want to enable and how to configure them.

.. code-block:: json

    {
       "zero_optimization": {
           "stage": 2,
           "allgather_partitions": true,
           "allgather_bucket_size": 5e8,
           "overlap_comm": true,
           "reduce_scatter": true,
           "reduce_bucket_size": 5e8,
           "contiguous_gradients": true,
           "cpu_offload": true
       }
    }

Notes:

- enabling ``cpu_offload`` should reduce GPU RAM usage (it requires ``"stage": 2``)
- ``"overlap_comm": true`` trades off increased GPU RAM usage to lower all-reduce latency. ``overlap_comm`` uses 4.5x
  the ``allgather_bucket_size`` and ``reduce_bucket_size`` values. So if they are set to 5e8, this requires a 9GB
  footprint (``5e8 x 2Bytes x 2 x 4.5``). Therefore, if you have a GPU with 8GB or less RAM, to avoid getting
  OOM-errors you will need to reduce those parameters to about ``2e8``, which would require 3.6GB. You will want to do
  the same on larger capacity GPU as well, if you're starting to hit OOM.
- when reducing these buffers you're trading communication speed to avail more GPU RAM. The smaller the buffer size,
  the slower the communication, and the more GPU RAM will be available to other tasks. So if a bigger batch size is
  important, getting a slightly slower training time could be a good trade.

This section has to be configured exclusively via DeepScale configuration - the :class:`~transformers.Trainer` provides
no equivalent command line arguments.



Optimizer
=======================================================================================================================


DeepScale's main optimizers are Adam, OneBitAdam, and Lamb. These have been thoroughly tested with ZeRO and are thus
recommended to be used. It, however, can import other optimizers from ``torch``. The full documentation is `here
<https://www.deepscale.khulnasoft.com/docs/config-json/#optimizer-parameters>`__.

If you don't configure the ``optimizer`` entry in the configuration file, the :class:`~transformers.Trainer` will
automatically set it to ``AdamW`` and will use the supplied values or the defaults for the following command line
arguments: ``--learning_rate``, ``--adam_beta1``, ``--adam_beta2``, ``--adam_epsilon`` and ``--weight_decay``.

Here is an example of the pre-configured ``optimizer`` entry for AdamW:

.. code-block:: json

    {
       "zero_allow_untested_optimizer": true,
       "optimizer": {
           "type": "AdamW",
           "params": {
             "lr": 0.001,
             "betas": [0.8, 0.999],
             "eps": 1e-8,
             "weight_decay": 3e-7
           }
         }
    }

Since AdamW isn't on the list of tested with DeepScale/ZeRO optimizers, we have to add
``zero_allow_untested_optimizer`` flag.

If you want to use one of the officially supported optimizers, configure them explicitly in the configuration file, and
make sure to adjust the values. e.g. if use Adam you will want ``weight_decay`` around ``0.01``.


Scheduler
=======================================================================================================================

DeepScale supports LRRangeTest, OneCycle, WarmupLR and WarmupDecayLR LR schedulers. The full documentation is `here
<https://www.deepscale.khulnasoft.com/docs/config-json/#scheduler-parameters>`__.

If you don't configure the ``scheduler`` entry in the configuration file, the :class:`~transformers.Trainer` will use
the value of ``--lr_scheduler_type`` to configure it. Currently the :class:`~transformers.Trainer` supports only 2 LR
schedulers that are also supported by DeepScale:

* ``WarmupLR`` via ``--lr_scheduler_type constant_with_warmup``
* ``WarmupDecayLR`` via ``--lr_scheduler_type linear``. This is also the default value for ``--lr_scheduler_type``,
  therefore, if you don't configure the scheduler this is scheduler that will get configured by default.

In either case, the values of ``--learning_rate`` and ``--warmup_steps`` will be used for the configuration.

In other words, if you don't use the configuration file to set the ``scheduler`` entry, provide either:

.. code-block:: bash

    --lr_scheduler_type constant_with_warmup --learning_rate 3e-5 --warmup_steps 500

or

.. code-block:: bash

    --lr_scheduler_type linear --learning_rate 3e-5 --warmup_steps 500

with the desired values. If you don't pass these arguments, reasonable default values will be used instead.

In the case of WarmupDecayLR ``total_num_steps`` gets set either via the ``--max_steps`` command line argument, or if
it is not provided, derived automatically at run time based on the environment and the size of the dataset and other
command line arguments.

Here is an example of the pre-configured ``scheduler`` entry for WarmupLR (``constant_with_warmup`` in the
:class:`~transformers.Trainer` API):

.. code-block:: json

    {
       "scheduler": {
             "type": "WarmupLR",
             "params": {
                 "warmup_min_lr": 0,
                 "warmup_max_lr": 0.001,
                 "warmup_num_steps": 1000
             }
         }
    }

Automatic Mixed Precision
=======================================================================================================================

You can work with FP16 in one of the following ways:

1. Pytorch native amp, as documented `here <https://www.deepscale.khulnasoft.com/docs/config-json/#fp16-training-options>`__.
2. NVIDIA's apex, as documented `here
   <https://www.deepscale.khulnasoft.com/docs/config-json/#automatic-mixed-precision-amp-training-options>`__.

If you want to use an equivalent of the Pytorch native amp, you can either configure the ``fp16`` entry in the
configuration file, or use the following command line arguments: ``--fp16 --fp16_backend amp``.

Here is an example of the ``fp16`` configuration:

.. code-block:: json

    {
        "fp16": {
            "enabled": true,
            "loss_scale": 0,
            "loss_scale_window": 1000,
            "hysteresis": 2,
            "min_loss_scale": 1
        },
    }

If you want to use NVIDIA's apex instead, you can can either configure the ``amp`` entry in the configuration file, or
use the following command line arguments: ``--fp16 --fp16_backend apex --fp16_opt_level 01``.

Here is an example of the ``amp`` configuration:

.. code-block:: json

    {
        "amp": {
            "enabled": true,
            "opt_level": "O1"
        }
    }



Gradient Clipping
=======================================================================================================================

If you don't configure the ``gradient_clipping`` entry in the configuration file, the :class:`~transformers.Trainer`
will use the value of the ``--max_grad_norm`` command line argument to set it.

Here is an example of the ``gradient_clipping`` configuration:

.. code-block:: json

    {
        "gradient_clipping": 1.0,
    }



Notes
=======================================================================================================================

* DeepScale works with the PyTorch :class:`~transformers.Trainer` but not TF :class:`~transformers.TFTrainer`.
* While DeepScale has a pip installable PyPI package, it is highly recommended that it gets installed from `source
  <https://github.com/khulnasoft/deepscale#installation>`__ to best match your hardware and also if you need to enable
  certain features, like 1-bit Adam, which aren't available in the pypi distribution.
* You don't have to use the :class:`~transformers.Trainer` to use DeepScale with HuggingFace ``transformers`` - you can
  use any model with your own trainer, and you will have to adapt the latter according to `the DeepScale integration
  instructions <https://www.deepscale.khulnasoft.com/getting-started/#writing-deepscale-models>`__.

Main DeepScale Resources
=======================================================================================================================

- `Project's github <https://github.com/khulnasoft/deepscale>`__
- `Usage docs <https://www.deepscale.khulnasoft.com/getting-started/>`__
- `API docs <https://deepscale.readthedocs.io/en/latest/index.html>`__
- `Blog posts <https://www.khulnasoft.com/en-us/research/search/?q=deepscale>`__

Papers:

- `ZeRO: Memory Optimizations Toward Training Trillion Parameter Models <https://arxiv.org/abs/1910.02054>`__
- `ZeRO-Offload: Democratizing Billion-Scale Model Training <https://arxiv.org/abs/2101.06840>`__

Finally, please, remember that, HuggingFace :class:`~transformers.Trainer` only integrates DeepScale, therefore if you
have any problems or questions with regards to DeepScale usage, please, file an issue with `DeepScale GitHub
<https://github.com/khulnasoft/DeepScale/issues>`__.
