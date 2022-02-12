#%%
from typing import List
import pandas as pd
import json
import os, getpass
import random
import spacy
from tqdm import tqdm
from argparse import ArgumentParser
from utils import get_paradir_path, space_before_eos
from pprint import pprint
from collections import Counter
#%%
# environment setting
def set_config(args) -> None:
    tqdm.pandas()
    setproctitle(args.proc_title)  # set the pid

def load_tokenizer(args):
    tokenizer = spacy.load(
        "en_core_web_sm",  # set the tokenizer
    )
    if args.gpu: spacy.prefer_gpu(args.device_id)  # set gpu id
    return tokenizer

def load_excel(file_path: str, args) -> pd.DataFrame:
    """
    It fetches Excel files and outputs them as Pandas.
    """
    dataset_path = get_paradir_path(file_path, args.debug)
    dataset = pd.read_excel(dataset_path, engine="openpyxl")
    return dataset


def preprocess_dataset(args, tokenizer) -> None:
    """
    After loading the dataset, pre-process the lowercase and space the eos.
    And output the dataset as an Excel file.
    """
    # load dataset
    trans = load_excel("data/translation_eng_kor(fixed).xlsx", args)

    trans["번역문"] = trans["번역문"].progress_apply(lambda text : space_before_eos(text,tokenizer))
    trans.to_excel(get_paradir_path("data/translation_eng_kor_eos(fixed).xlsx", args.debug))


def get_topk_situation(dataset: pd.DataFrame, k: int) -> List:
    """
    This function outputs the top k situations based on the number of conversation turns.
    For data matching, data work is performed on the top k situations with a large number of conversation turns.
    """
    situ_count = dataset.groupby("상황").count().sort_values(by="소분류", ascending=False)
    situ_count["대화수"] = situ_count["번역문"] / 4
    situations = situ_count.head(k).index.tolist()  # 대화수 상위 15개의 상황
    return situations


def sample_candidate(candidates: List, num: int = 18) -> List:
    """
    Create a candidate sentence used to predict the next utterance answer.
    Samples 18 from candidates in different situations.

    """
    return random.sample(candidates, num)


def load_dataset(args, tokenizer):
    """
    The data set in which the preprocessing operation is completed and the data set labeled with the situation are retrieved, and preprocessing is performed.
    The output result is in dictionary form.

    returns :
        Dict
    example:
        situation: ['<speaker1>','<speaker2>','<speaker1>','<speaker2>']
    """
    # dataset reload
    dialogue = load_excel("data/translation_eng_kor_eos(fixed).xlsx", args)
    # load situation labels
    situation_data_path = args.situation_data if args.situation_data else "data_processing/situation_label.json"
    situation_label_path = get_paradir_path(
        situation_data_path, args.debug
    )
    with open(situation_label_path) as fp:
        situation_labels = json.load(fp)

    # preprocessing: space the punctuation in <eos>
    for situation, descriptions in situation_labels.items():
        situation_labels[situation] = [space_before_eos(description, tokenizer) for description in descriptions]
    return dialogue, situation_labels

def duplication_in_label(labels: List[str]) -> List[str]:
    """
    This function checks the duplication of the situation label.
    """
    label_counts = Counter(labels).items()
    duplicated_labels = {label: count for label, count in label_counts if count > 1}
    return duplicated_labels


def match_situation(args, tokenizer) -> List[dict]:
    """ Match conversation with situation label. """
    dataset = []
    situation_duplication = []
    dialogue, situation_labels = load_dataset(args, tokenizer)
    for situation_label, persona in situation_labels.items():
        table = str.maketrans({"(":r"\(", ")": r"\)"})
        situation_label = situation_label.translate(table)


        is_contain = lambda text: dialogue[dialogue["상황"].str.contains(text)]
        is_not_contain = lambda text: dialogue[~dialogue["대분류"].str.contains(text)]

        situation = is_contain(situation_label)
        situation_duplication.extend(situation['상황'].unique().tolist())

        pprint(situation['상황'].unique())
        top_level = is_contain(situation_label)["대분류"].iloc[0]
        candidates = is_not_contain(top_level)["번역문"].to_list() # negative sampling for next utterance
        conversations = situation.groupby("Set Nr.")["번역문"].apply(list).tolist()

        for conversation in conversations:
            utterances = []
            if len(conversation) != 4:
                continue
            for i in range(len(conversation) - 1):
                candidate = sample_candidate(candidates) + [conversation[i + 1]]
                utterances.append(
                    {"candidates": candidate, "history": conversation[: i + 1]}
                )
            dialogue_entry = {"personality": persona, "utterances": utterances}
            dataset.append(dialogue_entry)

    return dataset

def match_situation_by_persona(args, tokenizer) -> List[dict]:
    """
    Match conversation with situation label.
    No divergence persona
    """

    dataset = []
    dialogue, situation_labels = load_dataset(args, tokenizer)
    for situation_label, persona in situation_labels.items():
        table = str.maketrans({"(": r"\(", ")": r"\)"})
        situation_label = situation_label.translate(table)
        # situation_label = situation_label.replace("(", r"\(")

        is_contain = lambda text: dialogue[dialogue["상황"].str.contains(text)]
        is_not_contain = lambda text: dialogue[~dialogue["대분류"].str.contains(text)]

        situation = is_contain(situation_label)
        top_level = is_contain(situation_label)["대분류"].iloc[0]
        candidates = is_not_contain(top_level)["번역문"].to_list()
        conversations = situation.groupby("Set Nr.")["번역문"].apply(list).tolist()

        dialogue_entry = {"personality": persona, "utterances": []}
        for conversation in conversations:
            utterances = []
            for i in range(len(conversation) - 1):
                candidate = sample_candidate(candidates) + [conversation[i + 1]]
                utterances.append(
                    {"candidates": candidate, "history": conversation[: i + 1]}
                )
            assert utterances == [], 'no match situation'
            dialogue_entry['utterances'] += utterances
        dataset.append(dialogue_entry)
    return dataset


def save_dataset(file_name :str , dataset: dict, shuffle=False, split=0.8):
    """ Shuffle and split the dataset. """
    random.shuffle(dataset) if shuffle else None
    # index = int(len(dataset) * split)
    index = len(dataset) - 1000
    dataset_file = {"train": dataset[:index], "valid": dataset[index:]}
    with open(f"data/{file_name}.json", "w+") as fp:
        json.dump(dataset_file, fp, indent=4)


def build():
    parser = ArgumentParser()
    parser.add_argument("--situation_data", type=str, default="data_processing/situation_annotation.json")
    parser.add_argument("--debug", type=bool, default=True, help="De˝bugging option for relative path.")
    parser.add_argument("--gpu", type=bool, default=False, help="Device ID for Spacy tokenizer.")
    parser.add_argument("--device_id", type=int, default=4, help="Device ID for Spacy tokenizer.")
    parser.add_argument("--proc_title", type=str, default=f"{getpass.getuser()}_persona", help="Name process ID title. ")
    args = parser.parse_args()

    # set_config(args)
    tokenizer = load_tokenizer(args)
    # preprocess_dataset(args, tokenizer)
    dataset = match_situation(args, tokenizer)
    save_dataset(file_name = "situationchat_original(augmented)", dataset = dataset)
    return dataset


#%%
if __name__ == "__main__":
    build()

