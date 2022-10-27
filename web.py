import random
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Union
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

from custom_chat import *
from situation_example import SITUATIONS, SITUATIONS_KEY


@dataclass
class PageConfig:
    page_title: str = "PEEP-Talk Demo"
    page_icon = Image.open("./statics/logo.png")
    layout: str = "centered"


hide_element: str = """<style>header {visibility: hidden;} footer {visibility: hidden;}</style>"""

st.set_page_config(**asdict(PageConfig()))
st.markdown(hide_element, unsafe_allow_html=True)


# URL = "http://nlplab.iptime.org:9060/"
URL = "http://nlplab.iptime.org:9045/"  # TEST


@dataclass
class Feedback:
    situation: float
    ling: float
    gec: str


@dataclass
class Message:
    message: str
    is_user: bool
    avatar_style: Optional[str] = None
    seed: Optional[int] = 243355423

    def __post_init__(self):
        if self.avatar_style is None:
            self.avatar_style = "personas" if self.is_user else "bottts"

    def to_dict(self):
        return asdict(self)

    def to_streamlit(self):
        return st_message(**self.to_dict())


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


def get_personality():
    personality = requests.get(urljoin(URL, "personality")).json()
    personality = map(lambda string: string.capitalize(), personality)
    return personality


if "chatbot" not in st.session_state:
    st.session_state["personality"] = []
    st.session_state["human"] = []
    st.session_state["chatbot"] = []
    st.session_state["gec"] = []
    st.session_state["feedback"] = []

    st.session_state["sim_score"] = 0
    st.session_state["accept_score"] = 0
    st.session_state["new_option"] = ""

    res = requests.get(urljoin(URL, "history/clear"))
    print(res.json())


# Header
st.image("./statics/logo.png", width=100)
st.subheader("PEEP-Talk+")


# Header Situation
option_col, bttn_col1, bttn_col2 = st.columns([4, 2, 2])

# Situation options and buttons
with option_col:
    st.markdown("**Situation**")
    option = st.selectbox(
        "Select the situation",
        options=SITUATIONS,
        help="Select the situation to start the conversation",
        index=0,
    )


if option != st.session_state["new_option"]:
    res = requests.get(urljoin(URL, "history/clear"))
    st.session_state.human = []
    st.session_state.chatbot = []
    st.session_state["gec"] = []
    st.session_state["new_option"] = option
    st.session_state["sim_score"] = 0
    st.session_state["accept_score"] = 0


def display_cd(sim_score: int, accept_score: int, sim_delta=0, accept_delta=0):
    with bttn_col1:
        st.subheader("CD Score")
        st.metric(label="Situation Similarity", value=f"{sim_score}%", delta=f"{sim_delta}%", delta_color="inverse")

    with bttn_col2:
        st.subheader("‎")
        st.metric(label="Linguistic Acceptability", value=f"{accept_score}%", delta=f"{accept_delta}%", delta_color="inverse")


gec_container = st.container()

human_input = st.text_input(
    "Talk to the chatbot",
    key="human_input",
    help=None,
    placeholder="My name are john",
    value="",
)

chat_container = st.container()

if human_input:
    input_json = {
        "user_input": human_input,
        "personality": SITUATIONS[option],
        "personality_index": SITUATIONS_KEY[option],
    }
    bot_res = requests.post(urljoin(URL, "message"), json=input_json).json()
    bot_msg = Message(message=bot_res["message"], is_user=False)

    feedback = Feedback(
        situation=round(bot_res["similarity"], 2),
        ling=round(bot_res["acceptability"], 2),
        gec=bot_res["correction"],
    )

    human_msg = Message(
        message=human_input,
        is_user=True,
    )

    bot_msg = Message(
        message=bot_res["message"],
        is_user=False,
    )

    with gec_container:
        st.markdown("**GEC**")
        st_annotate(*highlight_correction(human_input, bot_res["correction"]))
        st.write("\n")

    with chat_container:
        user_message = highlight_error(human_input, bot_res["correction"])
        user_message = render_message(user_message, is_user=True)
        st.markdown(user_message, unsafe_allow_html=True)

        st_message(**asdict(bot_msg))


# # input user text
# with st.form(key="user_form", clear_on_submit=True):
#     user_input = st.text_input(label="Type a message")
#     submit_button = st.form_submit_button(label="Submit")

#     if submit_button:
#         st.session_state["human"].append(user_input)
#         response = requests.post(
#             urljoin(URL, "message"),
#             json={
#                 "user_input": user_input,
#                 "personality": SITUATIONS[option],
#                 "personality_index": SITUATIONS_KEY[option],
#             },
#         ).json()
#         st.session_state["chatbot"].append(response["message"])
#         st.session_state["gec"].append(response["correction"])


# # messsage box
# if submit_button:
#     with dialogue_container.form(key="bot_form"):
#         display_dialogue()
#         sim_score = round(response["similarity"], 2)
#         accept_score = round(response["acceptability"], 2)

#         sim_delta = round((sim_score - st.session_state.sim_score), 2)
#         accept_delta = round((accept_score - st.session_state.accept_score), 2)

#         st.session_state.sim_score = sim_score
#         st.session_state.accept_score = accept_score

#         reset_button = st.form_submit_button(
#             label="",
#             on_click=diplay_cd(sim_score, accept_score, sim_delta, accept_delta),
#         )
