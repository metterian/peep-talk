import re
import requests


def text_preprocess(text:str, output = False)-> str:
    if not output:
        text = text.lower()
        text = re.sub(r"([?.!,:;¿])", r" \1 ", text)
        text = re.sub(r'[" "]+', " ", text)
    else:
        text = re.sub(r" ([?.!,:،؛؟¿])", r"\1", text)
        text = text.replace("▁"," ")
    return text

def correct(source: str) -> dict:
    language = "en-en"
    URL = "http://nlplab.iptime.org:32293/translator/translate"
    headers = {"Content-Type": "application/json"}
    query = [{"src": source, "id": language}]
    response = requests.post(URL, json=query, headers=headers)
    correction = response.json()[0][0]['tgt']
    correction = text_preprocess(correction, output = True)
    return correction
