import random
from dataclasses import dataclass, field
from typing import ClassVar, List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class ContextDetector:
    """Parent class for Context Similarity and Lingustic Acceptability for initialzing"""

    flag: bool = False

    def __init__(self, model_name) -> None:
        self.score = []
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.model.to(self.device)


class SituationSimilarity(ContextDector):
    """Get similarity between personality and history using fine-tuned model by MRPC dataset"""

    def __init__(self, model_name="textattack/xlnet-base-cased-MRPC") -> None:
        super().__init__(model_name)

    def predict(self, history: list, history_sentences: list):
        sentence = history[-1]  # recent human input
        scores = []

        for history_sentence in history_sentences:
            paraphrase = self.tokenizer.encode_plus(sentence, history_sentence, return_tensors="pt").to(self.device)
            paraphrase_classification_logits = self.model(**paraphrase)[0]
            paraphrase_results = torch.softmax(paraphrase_classification_logits, dim=1).tolist()[0]
            scores.append(float(paraphrase_results[1]))  # classes = ["not paraphrase", "is paraphrase"]

        scores = np.array(scores)
        score_max = np.max(scores)
        self.score.append(score_max * 100)
        return score_max * 100


class LinguisticAcceptability(ContextDector):
    """Get a score on how linguistically acceptable a user's input sentence using fine-tuned by CoLA dataset"""

    def __init__(self, model_name="textattack/roberta-base-CoLA") -> None:
        super().__init__(model_name)

    def predict(self, history):
        sentence = history[-1]
        paraphrase = self.tokenizer(sentence, return_tensors="pt").to(self.device)
        paraphrase_classification_logits = self.model(**paraphrase)[0]
        paraphrase_results = torch.softmax(paraphrase_classification_logits, dim=1).tolist()[0]
        self.score.append(float(paraphrase_results[1] * 100))
        return float(paraphrase_results[1] * 100)
