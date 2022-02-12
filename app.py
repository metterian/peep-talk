from dataclasses import dataclass
from typing import Optional, List
from fastapi import FastAPI
import uvicorn
from fastapi.params import Query

from models.context_detector import SituationSimilarity, LinguisticAcceptability
from models.chatbot import Chatbot
from models.config import args
from models import grammar


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
    user_input: str


app = FastAPI()
chatbot = Chatbot()
similarity = SituationSimilarity()
linguistic = LinguisticAcceptability()


@app.post("/message/")
async def message(item: Message):
    raw_text = item.user_input
    sentence = raw_text.strip()

    message = chatbot.send(sentence)
    human_history = chatbot.get_human_history()
    gold_history = chatbot.get_gold_history()

    similarity_score = similarity.predict(human_history, gold_history)
    lang_score = linguistic.predict(human_history)
    correction = grammar.correct(sentence)

    if int(similarity_score) < 15:
        message = "Why don't we speak another situation? \nPlease, click the switch button!"

    response = Response(
        message=message,
        similarity=similarity_score,
        acceptability=lang_score,
        personality=chatbot.get_personality(),
        correction=correction,
    )
    persona_string = '\n'.join(chatbot.get_personality())
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
    uvicorn.run(app, host="0.0.0.0", port=9060)
