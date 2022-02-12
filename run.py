from models.context_detector import ContextSimilarity, LinguisticAcceptability
from models.chatbot import Chatbot
from models.config import args
from models import grammar

from typing import List
import torch
import json
import os
from pprint import pprint


chatbot = Chatbot()
MRPC = ContextSimilarity()
CoLA = LinguisticAcceptability()


turn_flag = False
turn = 0
threshold_sim = 25
threshold_cor = 75


class History:
    def __init__(self, model) -> None:
        self.model = model
        self.human = self.model.get_human_history()
        self.chatbot = self.model.get_chatbot_history()

    def __repr__(self) -> str:
        return f'Human: {self.human} \nChatbot: {self.chatbot}'

    def clear(self):
        self.model.clear_history()
        self.human = []

isChanged = False
while True:
    raw_text = input(">>> ")
    sentence = raw_text.strip()

    # predict next sentence
    message = chatbot.send_message(sentence)
    human_history = chatbot.get_human_history()
    gold_history = chatbot.get_gold_history()

    similarity = MRPC.predict(human_history, gold_history)
    acceptability = CoLA.predict(human_history)

    result_spell = grammar.correct(sentence)

    # When you got response from chatbot >> turn +1
    turn += 1

    if turn >= 2:
        if similarity < threshold_sim or acceptability < threshold_cor:
            chatbot.shuffle()
            chatbot.clear_history()
            isChanged = True
            turn = 0

    results = {
        "message": message,
        "similarity": similarity,
        "acceptability": acceptability,
        "persona": chatbot.get_personality(),
        "turn": turn,
        "spell": result_spell if result_spell.lower() != sentence else ["nothing to change!"],
        "persona_changed" : isChanged
    }

    # if AFL.count >= 4:  ## 나중에 5턴
    #     CoLA_avg = CoLA.average()
    #     MRPC_avg = MRPC.average()

    #     if CoLA_avg > 70 and MRPC_avg > 65 and AFL.changed_flag == False:
    #         shuffle_idx = random.choice(range(len(personalities)))
    #         personality = personalities[shuffle_idx]
    #         history_original = history[shuffle_idx]
    #         history_original = [tokenizer.decode(line) for line in history_original]
    #         chatbot.personality = personality
    #         chatbot.hisory = []

    #         AFL.count = 0


    #     chatbot.history = []


    # pprint(results)  # 받아온 데이터를 다시 전송
    print(json.dumps(results, indent=4))


