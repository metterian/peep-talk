import os
import pickle
import random
from abc import *
from typing import List

import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from interact import sample_sequence
from models.config import args
from train import add_special_tokens_
from utils import get_dataset


def pickle_load(path: str):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data


def pickle_save(path: str, data) -> None:
    with open(path, "wb") as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def load_dataset(args, tokenizer) -> None:
    """Load Persona, History dataset as caches or json files"""
    dataset = get_dataset(tokenizer, args.dataset_path, args.dataset_cache)
    personalities = [dialog["personality"] for dataset in dataset.values() for dialog in dataset]
    utterances = [dialog["utterances"] for dataset in dataset.values() for dialog in dataset]

    return personalities, utterances, dataset


def find_dialog_history(personality, dataset):
    gold_history = []
    for dataset in dataset.values():
        for dialog in dataset:
            if dialog["personality"] == personality:
                gold_history.extend(dialog["utterances"][-1]["history"])
    return gold_history


def shuffle_inputs(personalities, utterances, dataset):
    """Shuffle the inputs which are persona, utterance and history by the persona index"""
    shuffle_idx = random.choice(range(len(personalities)))
    personality = personalities[shuffle_idx]
    utterance = utterances[shuffle_idx]
    gold_history = find_dialog_history(personality, dataset)
    return personality, utterance, gold_history


class Chatbot:
    """Conversation Agent model based on Hugging face, using GPT-2"""

    def __init__(self) -> None:
        """Initialize tokenizer, model and datasets"""
        if args.seed != 0:
            random.seed(args.seed)
            torch.random.manual_seed(args.seed)
            torch.cuda.manual_seed(args.seed)

        # laod tokenizer and model
        tokenizer_class, model_class = GPT2Tokenizer, GPT2LMHeadModel
        self.tokenizer = tokenizer_class.from_pretrained(args.model_checkpoint)
        self.model = model_class.from_pretrained(args.model_checkpoint)
        self.model.to(args.device)
        add_special_tokens_(self.model, self.tokenizer)

        # load dataset
        self.personalities, self.utterances, self.dataset = load_dataset(args, self.tokenizer)

        # set personality as shuffling
        self.personality, self.utterance, self.gold_history = shuffle_inputs(self.personalities, self.utterances, self.dataset)

        # set history as empty list for recording the conversation
        self.history = []

    def send(self, personality: List[str], sentence: str) -> str:
        """Receive user input(sentence) with Persona and send the next utterance."""
        self.history.append(self.tokenizer.encode(sentence))
        self.personality = [self.tokenizer.encode(p) for p in personality]
        print("SMAPLE:", self.personality)
        with torch.no_grad():
            out_ids = sample_sequence(self.personality, self.history, self.tokenizer, self.model, args)
            self.history.append(out_ids)
            self.history = self.history[-(2 * args.max_history + 1) :]
            out_text = self.tokenizer.decode(out_ids, skip_special_tokens=True)
        return out_text

    def shuffle(self) -> None:
        self.personality, self.utterance, self.gold_history = shuffle_inputs(self.personalities, self.utterances, self.dataset)

    def decode(self, tokens: List[List[str]]) -> List[str]:
        "Decode the double list by tokenizer"
        return [self.tokenizer.decode(token) for token in tokens]

    def get_personality(self) -> List[str]:
        """Return current personality"""
        personality_decoded = self.decode(self.personality)
        print(f"PERSONA:{personality_decoded}")
        return personality_decoded

    def get_history(self) -> List[str]:
        return self.history_decoded

    def get_human_history(self) -> List[str]:
        """Return divide history and get human dialogue"""
        history = self.decode(self.history)
        return history[::2]

    def get_chatbot_history(self) -> List[str]:
        """Return divide history and get chatbot dialogue"""
        history = self.decode(self.history)
        self.chatbot_history = history
        return history[1::2]

    def get_gold_history(self) -> List[List[str]]:
        max_idx = len(self.gold_history) if len(self.gold_history) < 50 else 50
        # return self.decode(self.gold_history[:max_idx])
        return self.decode(self.gold_history)

    def clear_history(self) -> None:
        """Clear the history"""
        self.history = []

    @property
    def len_history(self) -> int:
        return len(self.history)
