import os
import spacy


def get_paradir_path(path: str, debug: bool) -> str:
    """
    Get the file path including parents path
        - debug : for debugging option
    """

    return os.path.join(os.path.pardir, path) if not debug else path


def check_punctuation(words):
    """Check to see if there's a period in the sentence."""
    punctuation = [".", ",", "?"]
    return [word for word in words if word in punctuation]


# preprocess the text
def space_before_eos(sentence: str, tokenizer):
    """
    Preprocessing function:
        - Spaces before periods at end of sentences
        - everything lowercase
    """
    table = str.maketrans({".": " .", ",": " ,", "?":" ?"})
    sentence = sentence.lower().split()
    for i, word in enumerate(sentence):
        if check_punctuation(word):
            for token in tokenizer(word):
                if token.pos_ == "PUNCT":
                    sentence[i] = sentence[i].translate(table)
    return " ".join(sentence)
