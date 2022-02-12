from easydict import EasyDict as edict
import torch

args = edict(
    {
        "model": "gpt2",
        "dataset_path": "./data/situationchat_original.json",
        "dataset_cache": "./situationchat_original_dataset_cache_GPT2Tokenizer",
        "model_checkpoint": "./experiments/Jan20_15-41-22_microsoft/DialoGPT-large/",
        "temperature": 0.7,
        "top_k": 0,
        "top_p": 0.9,
        "max_history": 2,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "no_sample": True,
        "max_length": 20,
        "min_length": 1,
        "seed": 0,
    }
)
