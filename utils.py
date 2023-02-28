# Copyright (c) 2019-present, HuggingFace Inc.
# All rights reserved. This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
import json
import logging
import os
import re
import socket
import tarfile
import tempfile
from datetime import datetime

import torch

# from transformers import cached_path

PERSONACHAT_URL = "https://s3.amazonaws.com/datasets.huggingface.co/personachat/personachat_self_original.json"
HF_FINETUNED_MODEL = "https://s3.amazonaws.com/models.huggingface.co/transfer-learning-chatbot/gpt_personachat_cache.tar.gz"

logger = logging.getLogger(__file__)


def get_logger(output_log_path=None):
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    if output_log_path is not None:
        file_handler = logging.FileHandler(output_log_path)
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    if output_log_path is not None:
        logger.addHandler(file_handler)

    return logger


def download_pretrained_model():
    """Download and extract finetuned model from S3"""
    resolved_archive_file = cached_path(HF_FINETUNED_MODEL)
    tempdir = tempfile.mkdtemp()
    logger.info("extracting archive file {} to temp dir {}".format(resolved_archive_file, tempdir))
    with tarfile.open(resolved_archive_file, "r:gz") as archive:
        archive.extractall(tempdir)
    return tempdir


def get_dataset(tokenizer, dataset_path, dataset_cache):
    """Get tokenized PERSONACHAT dataset from S3 or cache."""
    dataset_path = dataset_path or PERSONACHAT_URL
    dataset_name = os.path.basename(dataset_path).replace(".json", "")
    # dataset_cache = dataset_name + '_' + dataset_cache + '_' + type(tokenizer).__name__  # To avoid using GPT cache for GPT-2 and vice-versa
    dataset_cache = (
        dataset_name + "_" + "dataset_cache" + "_" + type(tokenizer).__name__
    )  # To avoid using GPT cache for GPT-2 and vice-versa
    if dataset_cache and os.path.isfile(dataset_cache):
        logger.info("Load tokenized dataset from cache at %s", dataset_cache)
        dataset = torch.load(dataset_cache)
    else:
        logger.info("Download dataset from %s", dataset_path)
        personachat_file = cached_path(dataset_path)
        with open(personachat_file, "r", encoding="utf-8") as f:
            dataset = json.loads(f.read())

        logger.info("Tokenize and encode the dataset")

        def tokenize(obj):
            if isinstance(obj, str):
                return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(obj))
            if isinstance(obj, dict):
                return dict((n, tokenize(o)) for n, o in obj.items())
            return list(tokenize(o) for o in obj)

        dataset = tokenize(dataset)
        torch.save(dataset, dataset_cache)
    return dataset


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def make_logdir(model_name: str):
    """Create unique path to save results and checkpoints, e.g. runs/Sep22_19-45-59_gpu-7_gpt2"""
    # Code copied from ignite repo
    current_time = datetime.now().strftime("%b%d_%H-%M-%S")
    logdir = os.path.join("experiments", current_time + "_" + model_name)
    return logdir


def text_preprocess(text: str, output=False) -> str:
    if not output:
        text = text.lower()
        text = re.sub(r"([?.!,:;¿])", r" \1 ", text)
        text = re.sub(r'[" "]+', " ", text)
    else:
        text = re.sub(r" ([?.!,:،؛؟¿])", r"\1", text)
        text = text.replace("▁", " ")
    return text
