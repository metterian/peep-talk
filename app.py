import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import numpy as np
import requests
import torch
import uvicorn
from fastapi import FastAPI
from fastapi.params import Query
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from chatbot import STS_URL
from interact import sample_sequence
from models.config import args
from models.context_detector import LinguisticAcceptability, SituationSimilarity
from models.conversation import Chatbot
from situation_info import anno_to_situ, situ_to_anno
from train import add_special_tokens_
from utils import get_logger

logger = get_logger()
os.environ["CUDA_VISIBLE_DEVICES"] = "1"


class ConvModule:
    def __init__(self) -> None:
        self.model = GPT2LMHeadModel.from_pretrained(args.model_checkpoint).cuda()
        self.tokenizer = GPT2Tokenizer.from_pretrained(args.model_checkpoint)
        add_special_tokens_(self.model, self.tokenizer)

    def generate(self, situation: List[str], history: List[str]) -> str:
        logger.info("Selected situation: %s", situation)

        tokenized_situation = [self.tokenizer.encode(s) for s in situation]
        tokenized_history = [self.tokenizer.encode(s) for s in history[-(2 * args.max_history + 1) :]]

        with torch.no_grad():
            out_ids = sample_sequence(
                personality=tokenized_situation,
                history=tokenized_history,
                tokenizer=self.tokenizer,
                model=self.model,
                args=args,
            )
        out_text = self.tokenizer.decode(out_ids, skip_special_tokens=True)

        return out_text


def correct(source: str) -> dict:
    URL = "http://nlplab.iptime.org:9066/message/"
    headers = {"accept": "application/json"}
    data = {"sentence": source}
    response = requests.post(URL, json=data, headers=headers)
    correction = response.json()["correction"]
    return correction


def load_situation_chat():
    """Load situation chat data"""
    situation_data = json.load(open("data/situationchat_original.json"))["train"]
    # count how many history in each situation
    situation_chat = {}
    for row in situation_data:
        situation = tuple(row["personality"])
        history = row["utterances"][-1]["history"] + [row["utterances"][-1]["candidates"][-1]]
        history = history

        if situation not in situation_chat:
            situation_chat[situation] = {"count": 0, "history": [history]}

        else:
            situation_chat[situation]["count"] += 1
            situation_chat[situation]["history"].extend([history])
    # sort by number of history
    situation_chat = dict(sorted(situation_chat.items(), key=lambda item: item[1]["count"], reverse=True)[:30])
    return situation_chat


def get_situ_hist_embeddings(model: SentenceTransformer, situation_chat: dict):
    """Get embeddings of situation history"""
    for situation, data in situation_chat.items():
        # double list to single list
        hist = [item for sublist in data["history"] for item in sublist]
        situation_chat[situation]["embedding"] = model.encode(hist)
    return situation_chat


def get_sim_score(sentence: str, model: SentenceTransformer, embeddings: dict):
    """Get similarity score between input sentence and situation history"""
    input_embedding = model.encode([sentence])
    sims = cosine_similarity(input_embedding, embeddings)
    max_score = np.max(sims)
    return float(max_score) * 100


def load_conv_module(model_name: str) -> tuple[GPT2LMHeadModel, GPT2Tokenizer]:
    model = GPT2LMHeadModel.from_pretrained(model_name).cuda()
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    add_special_tokens_(model, tokenizer)
    return model, tokenizer


@dataclass
class Response:
    """Response dataclass for API"""

    situation: str
    history: List[Union[Dict[str, str], Dict[str, bool]]]
    similarity: int
    acceptability: int
    correction: str


@dataclass
class Message:
    """
    Message dataclass for API

    Args:
        situation -> situation annotation
        history -> [{'text': "text", "is_user": True}, {'text': "text", "is_user": False}]
    """

    situation: str
    history: List[Dict[str, Union[bool, str]]]  # history of conversation


app = FastAPI()

sts_model = SentenceTransformer("sentence-transformers/stsb-roberta-base-v2", device="cuda")
situation_chat = load_situation_chat()
situation_chat = get_situ_hist_embeddings(sts_model, situation_chat)

chatbot = ConvModule()
linguistic = LinguisticAcceptability()


@app.post("/message/")
async def message(item: Message):
    annotation = item.situation
    situation = anno_to_situ[annotation]

    history = item.history
    history_text = [h["text"] for h in item.history]
    user_history = [h["text"] for h in item.history if h["is_user"]]  # raw_text is last user text
    user_input = user_history[-1]

    generated_text = chatbot.generate(situation, history_text)
    history.append({"text": generated_text, "is_user": False})

    situ_hist_embedding = situation_chat[situation]["embedding"]

    similarity_score = get_sim_score(user_input, sts_model, situ_hist_embedding)
    lang_score = linguistic.predict(user_input)
    correction = correct(user_input)

    if int(similarity_score) < 40 and len(user_history) >= 5:
        message = "Why don't we speak another situation? \nPlease, click the different situation 😇"

    response = Response(
        history=history,
        similarity=similarity_score,
        acceptability=lang_score,
        situation=situation,
        correction=correction,
    )
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9031)
    # uvicorn.run(app, host="0.0.0.0", port=9060)
