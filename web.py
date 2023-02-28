import json
import os
import random
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

import numpy as np
import requests
import streamlit as st
from annotated_text import annotated_text as st_annotate
from annotated_text import util
from htbuilder import H, HtmlElement, my_element, style, styles
from nltk.tokenize import word_tokenize
from PIL import Image
from streamlit_chat import message as st_message
from truecase import get_true_case

import streamlit_analytics
from custom_chat import *
from situation_info import anno_to_situ, situ_to_anno


@dataclass
class PageConfig:
    page_title: str = "PEEP-Talk Demo"
    page_icon = "🐤"
    layout: str = "centered"


@dataclass
class ChatMode:
    free_conv = "Free Conversation (자유대화)"
    practice = "Situation Practice (상황 교육 연습)"


hide_element: str = "<style>header {visibility: hidden;} footer {visibility: hidden;}</style>"

st.set_page_config(**asdict(PageConfig()))
st.markdown(hide_element, unsafe_allow_html=True)


# URL = "http://nlplab.iptime.org:9060/"
# URL = "http://nlplab.iptime.org:9045/"  # TEST
URL = "http://nlplab.iptime.org:9031/"  # Alpha


@dataclass
class Feedback:
    situation: float
    ling: float
    gec: str


@dataclass
class Message:
    is_user: bool
    text: str
    feedback: Optional[Feedback] = None
    avatar_style: Optional[str] = None
    seed: Optional[int] = 243355423

    def __post_init__(self):
        if self.avatar_style is None:
            self.avatar_style = "personas" if self.is_user else "bottts"

    # def to_dict(self):
    #     return asdict(self)

    def to_streamlit(self):
        return st_message(**self.to_dict())

    def to_dict(self):
        return {"text": self.text, "is_user": self.is_user}


def annotation(body, label="", background=None, color=None, **style):
    color_style = {}

    if color:
        color_style["color"] = color

    if not background:
        label_sum = sum(ord(c) for c in label)
        background_color = PALETTE[label_sum % len(PALETTE)]
        background_opacity = OPACITIES[label_sum % len(OPACITIES)]
        background = background_color + background_opacity

    return span(
        style=styles(
            background=background,
            border_radius=rem(0.5),
            padding=(rem(0.125), rem(0.33)),
            overflow="hidden",
            **color_style,
            **style,
        )
    )(
        html.escape(body),
        span(
            style=styles(
                text_transform="uppercase",
            )
        ),
    )


def annotate(text, color):
    return annotation(text, "", color)


def highlight_correction(original: str, correction: str):
    """highlight correction"""
    cor = word_tokenize(correction)
    ori = word_tokenize(original)
    for i, (c, o) in enumerate(zip(cor, ori)):
        if c != o:
            cor[i] = annotate(c, Color.green)
        else:
            cor[i] = c + " "
    return cor


def highlight_error(original: str, correction: str):
    """highlight error"""
    cor = word_tokenize(correction)
    ori = word_tokenize(original)
    for i, (c, o) in enumerate(zip(cor, ori)):
        if c != o:
            cor[i] = highlight(c, Color.red)
        else:
            cor[i] = c + " "
    return cor


def right_align(text, bold=False):
    return f"<p style='text-align: right;'>{text}</p>"


def bold(text):
    return f"<p style='text-align: right;'><b>{text}</b></p>"


def display_dialogue():
    """display between Human and Chatbot conversation"""

    for human, chatbot, cor_sen in zip(st.session_state.human, st.session_state.chatbot, st.session_state.gec):
        st.markdown(right_align(f"You: {human}"), unsafe_allow_html=True)
        st.write(f"Bot: {get_true_case(chatbot)}\n\nGEC: {cor_sen}")


@st.experimental_memo
def load_conv_data():
    with open("data/situationchat_original.json", "r") as f:
        data = json.load(f)
    return data


@st.experimental_memo
def load_situation_chat():
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


def display_cd(sim_score: int, accept_score: int, sim_delta=0, accept_delta=0):
    with bttn_col1:
        st.subheader("CD Score")
        st.metric(label="Situation Similarity", value=f"{sim_score}%", delta=f"{sim_delta}%", delta_color="inverse")

    with bttn_col2:
        st.subheader("‎")
        st.metric(label="Linguistic Acceptability", value=f"{accept_score}%", delta=f"{accept_delta}%", delta_color="inverse")


def clear_history():
    st.session_state.history = []
    st.session_state.text_input = ""
    st.session_state.expander = False


def header():
    st.image("./statics/logo.png", width=100)
    st.subheader("PEEP-Talk+")


situation_chat = load_situation_chat()
# TODO
if "situation" not in st.session_state:
    st.session_state["situation"] = list(anno_to_situ.keys())[0]
    situation = st.session_state.situation
    st.session_state["history"] = []
    st.session_state.text_input = ""
    st.session_state.expander = False

# * USER ID INPUT
# st.session_state["is_login"] = False

# if "user_id" not in st.session_state:
#     with st.form(key="user_id_form"):
#         st.text_input("전화 번호 뒷자리 4자리를 입력해주세요.", value="", max_chars=4, key="user_id")
#         submit_button = st.form_submit_button(label="입력")
#     st.session_state["history"] = []
#     st.session_state["is_login"] = True

# * Header
header()

#  define column
option_col, bttn_col1, bttn_col2 = st.columns([4, 2, 2])

streamlit_analytics.start_tracking()
with option_col:
    st.markdown("**Situation**")
    situation = list(anno_to_situ.keys())[0]
    st.selectbox(
        "Select the situation",
        options=list(anno_to_situ.keys()),
        help="Select the situation to start the conversation",
        key="situation",
        index=0,
        on_change=clear_history,
        # disabled=st.session_state.is_login,
    )

with st.expander("Hint for Situation 👩‍🏫", expanded=st.session_state.expander):
    st.write("**Situation:**", st.session_state.situation)
    situ_anno = anno_to_situ[st.session_state.situation]

    # situation_chat = load_situation_chat()
    random_num = random.randint(0, len(situation_chat[situ_anno]["history"]) - 1)
    random_history = situation_chat[situ_anno]["history"][random_num]

    sides = [False, True, False, True]
    for utterance, side in zip(random_history, sides):
        st_message(get_true_case(utterance), is_user=side)
    next_bttn = st.button("Next")
    if next_bttn:
        st.session_state.expander = True

gec_container = st.container()

# streamlit_analytics.start_tracking()
text_input = st.text_input(
    "Talk to the chatbot",
    key="text_input",
    help=None,
    placeholder="My name are john",
    value="",
    # disabled=st.session_state.is_login,
)
streamlit_analytics.stop_tracking(save_to_json="streamlit_analytics/text_input.json")

chat_container = st.container()

# * Text Input
if st.session_state.text_input:
    message = Message(text=st.session_state.text_input, is_user=True)

    st.session_state.history.append(message.to_dict())
    json_body = {
        "situation": st.session_state.situation,
        "history": st.session_state.history,
    }

    res = requests.post(urljoin(URL, "message"), json=json_body).json()
    st.session_state.history = res["history"]

    feedback = Feedback(
        situation=round(res["similarity"], 2),
        ling=round(res["acceptability"], 2),
        gec=res["correction"],
    )
    with gec_container:
        st.markdown("**Grammar Error Correction**")
        st_annotate(*highlight_correction(st.session_state.text_input, res["correction"]))
        st.write("\n")

    display_cd(round(res["similarity"], 2), round(res["acceptability"], 2), 0, 0)

# * Display chat history
if st.session_state.history:

    with chat_container:
        for i, msg in enumerate(st.session_state.history):
            # user's last message
            if msg["is_user"]:
                if msg["text"] == text_input:
                    message = highlight_error(msg["text"], res["correction"])
                    message = render_message(msg["text"], is_user=True)
                    st.markdown(message, unsafe_allow_html=True)
                else:
                    message = render_message(text=msg["text"], is_user=True)
                    st.markdown(message, unsafe_allow_html=True)

            else:
                st_message(message=get_true_case(msg["text"]), is_user=msg["is_user"], avatar_style="bottts", seed=43)
