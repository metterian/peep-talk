import streamlit as st
from typing import List
from truecase import get_true_case
import random
import requests
import numpy

from urllib.parse import urljoin

# URL = "http://nlplab.iptime.org:9060/"
URL = "http://nlplab.iptime.org:9045/" # TEST


SITUATIONS = {
    "School life (exams, vacation plans, admission, etc.)": [
        "i just took a quiz .",
        "i have a test .",
        "i have a family road trip planned for the western u.s.",
    ],
    "Customer consultation": [
        "i need to talk to the customer on the phone .",
        "the customer wants to cancel the payment .",
        "the customer wants to return it because of the product defect .",
    ],
    "Food and taste evaluation": [
        "i am eating food .",
        "i am evaluating after eating food .",
        "i am a food critic .",
    ],
    "Talk about your favorite team": [
        "my favorite player is the most passionate .",
        "the team has a pretty uniform .",
        "i think our team will win again this time .",
    ],
    "Job interview": [
        "i'm unemployed .",
        "i'm looking for a job .",
        "i'm having a job interview .",
    ],
    "In the cosmetics store": [
        "i want to buy eyeliner .",
        "i want to get a lipstick color recommendation .",
        "i'm in a new cosmetics store .",
    ],
    "Ask and answer symptoms": [
        "i came to the hospital because i was sick .",
        "i'm talking to a doctor about symptoms .",
        "i'm talking to a doctor at the hospital .",
    ],
    "Talk about the style you want": [
        "i came to the hair salon .",
        "i want to change my hairstyle .",
        "i'm talking to the clerk about the style i want .",
    ],
}


SITUATIONS_KEY = {
    "School life (exams, vacation plans, admission, etc.)": 0,
    "Customer consultation": 1,
    "Food and taste evaluation": 2,
    "Talk about your favorite team": 3,
    "Job interview": 4,
    "In the cosmetics store": 5,
    "Ask and answer symptoms": 6,
    "Talk about the style you want": 7,
}



def right_align(text, bold=False):
    return f"<p style='text-align: right;'>{text}</p>"


def bold(text):
    return f"<p style='text-align: right;'><b>{text}</b></p>"


def display_dialogue():
    """display between Human and Chatbot conversation"""
    # if not st.session_state.chatbot:
    #     return
    for human, chatbot, cor_sen in zip(
        st.session_state.human, st.session_state.chatbot, st.session_state.gec
    ):
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

    st.session_state["sim_score"] = 0
    st.session_state["accept_score"] = 0
    st.session_state['new_option'] = ''

    res = requests.get(urljoin(URL, "history/clear"))
    print(res.json())


st.image("./statics/logo.png", width=100)
st.title("PEEP-Talk")


# Header Situation


option_col, bttn_col1, bttn_col2 = st.columns([4, 2, 2])

# Situation options and buttons
with option_col:
    st.subheader("Situation")
    option = st.selectbox(
        "Select the situation",
        options=SITUATIONS,
        help="Select the situation to start the conversation",
        index=0,
    )


if option != st.session_state['new_option']:
    print(option)
    res = requests.get(urljoin(URL, "history/clear"))
    print(res.json())
    st.session_state.human = []
    st.session_state.chatbot = []
    st.session_state["gec"] = []
    st.session_state['new_option'] = option
    st.session_state['sim_score'] = 0
    st.session_state['accept_score'] = 0




def diplay_cd(sim_score: int, accept_score: int, sim_delta=0, accept_delta=0):
    with bttn_col1:
        st.subheader("CD Score")
        st.metric(
            label="Situation Similarity", value=f"{sim_score}%", delta=f"{sim_delta}%", delta_color='inverse'
        )

    with bttn_col2:
        st.subheader("‎")
        st.metric(
            label="Linguistic Acceptability",
            value=f"{accept_score}%",
            delta=f"{accept_delta}%",
            delta_color='inverse'
        )


dialogue_container = st.container()

# input user text
with st.form(key="user_form", clear_on_submit=True):
    user_input = st.text_input(label="Type a message")
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        st.session_state["human"].append(user_input)
        response = requests.post(
            urljoin(URL, "message"),
            json={
                "user_input": user_input,
                "personality": SITUATIONS[option],
                "personality_index": SITUATIONS_KEY[option],
            },
        ).json()
        st.session_state["chatbot"].append(response["message"])
        st.session_state["gec"].append(response["correction"])


# messsage box
if submit_button:
    with dialogue_container.form(key="bot_form"):
        # st.write('Bot')
        display_dialogue()
        sim_score = round(response["similarity"], 2)
        accept_score = round(response["acceptability"], 2)

        sim_delta = round((sim_score - st.session_state.sim_score), 2)
        accept_delta = round((accept_score - st.session_state.accept_score), 2)

        st.session_state.sim_score = sim_score
        st.session_state.accept_score = accept_score

        reset_button = st.form_submit_button(
            label="",
            on_click=diplay_cd(sim_score, accept_score, sim_delta, accept_delta),
        )
