from dataclasses import dataclass
from typing import Optional, List
from chatbot import STS_URL
from fastapi import FastAPI
import uvicorn
from fastapi.params import Query
import requests
from models.context_detector import SituationSimilarity, LinguisticAcceptability
from models.chatbot import Chatbot
from models.config import args



def correct(source: str) -> dict:
    URL = 'http://nlplab.iptime.org:9066/message/'
    headers = {'accept': 'application/json'}
    data = {"sentence": source}
    response = requests.post(URL, json=data, headers=headers)
    correction = response.json()['correction']
    return correction

@dataclass
class Response:
    message: str
    similarity: int
    acceptability: int
    personality: List[str]
    # turn: Optional[int]
    correction: str
    changed: Optional[bool] = False


@dataclass
class Message:
    personality: List[str]
    personality_index: int
    user_input: str


app = FastAPI()
chatbot = Chatbot()
# similarity = SituationSimilarity()
linguistic = LinguisticAcceptability()
# gec = GEC()


@app.post("/message/")
async def message(item: Message):
    raw_text = item.user_input
    personality = item.personality
    idx = item.personality_index
    sentence = raw_text.strip()

    print("INPUT: ", personality)

    message = chatbot.send(personality, sentence)


    similarity_score = requests.post(STS_URL, json={'index': idx, 'sentence': sentence}).json()['score']
    # similarity_score = similarity.predict(human_history, gold_history)
    lang_score = linguistic.predict(sentence)
    correction = correct(sentence)

    print("SIMILARITY SCORE: ", similarity_score)
    print("LENGTH: ", len(chatbot.history))
    if int(similarity_score) < 40 and len(chatbot.history) >= 5:
        message = "Why don't we speak another situation? \nPlease, click the different situation 😇"

    response = Response(
        message=message,
        similarity=similarity_score,
        acceptability=lang_score,
        personality=chatbot.get_personality(),
        correction=correction,
    )
    return response

@app.get("/personality/")
async def read_persona():
    return chatbot.get_personality()

@app.get('/personality/shuffle/')
async def shuffle_persona():
    chatbot.shuffle()
    return "Success"

@app.get('/history/clear')
async def clear_history():
    chatbot.clear_history()
    return "Success"

@app.get('/personality/swtich')
async def switch_perosna():
    chatbot.shuffle()
    chatbot.clear_history()
    return "Success"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9045)
    # uvicorn.run(app, host="0.0.0.0", port=9060)
