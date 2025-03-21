# coding=utf-8
# Copyright The HuggingFace Inc. team. All rights reserved.
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
"""Tokenization classes for ConvBERT."""
from ...utils import logging
from ..bert.tokenization_bert_fast import BertTokenizerFast
from .tokenization_convbert import ConvBertTokenizer

logger = logging.get_logger(__name__)

VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt"}

PRETRAINED_VOCAB_FILES_MAP = {
    "vocab_file": {
        "YituTech/conv-bert-base":
        "https://huggingface.co/YituTech/conv-bert-base/resolve/main/vocab.txt",
        "YituTech/conv-bert-medium-small":
        "https://huggingface.co/YituTech/conv-bert-medium-small/resolve/main/vocab.txt",
        "YituTech/conv-bert-small":
        "https://huggingface.co/YituTech/conv-bert-small/resolve/main/vocab.txt",
    }
}

PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES = {
    "YituTech/conv-bert-base": 512,
    "YituTech/conv-bert-medium-small": 512,
    "YituTech/conv-bert-small": 512,
}

PRETRAINED_INIT_CONFIGURATION = {
    "YituTech/conv-bert-base": {
        "do_lower_case": True
    },
    "YituTech/conv-bert-medium-small": {
        "do_lower_case": True
    },
    "YituTech/conv-bert-small": {
        "do_lower_case": True
    },
}


class ConvBertTokenizerFast(BertTokenizerFast):
    r"""
    Construct a "fast" ConvBERT tokenizer (backed by HuggingFace's `tokenizers` library).

    :class:`~transformers.ConvBertTokenizerFast` is identical to :class:`~transformers.BertTokenizerFast` and runs
    end-to-end tokenization: punctuation splitting and wordpiece.

    Refer to superclass :class:`~transformers.BertTokenizerFast` for usage examples and documentation concerning
    parameters.
    """

    vocab_files_names = VOCAB_FILES_NAMES
    pretrained_vocab_files_map = PRETRAINED_VOCAB_FILES_MAP
    max_model_input_sizes = PRETRAINED_POSITIONAL_EMBEDDINGS_SIZES
    pretrained_init_configuration = PRETRAINED_INIT_CONFIGURATION
    slow_tokenizer_class = ConvBertTokenizer
