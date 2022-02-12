#%%
import json
from tkinter import dialog

from attrs import setters
from datasets import DatasetBuilder
import pandas as pd



# %%
df = pd.read_excel('../data/translation_eng_kor(fixed).xlsx')
# %%
# %%
dial_count = df.groupby(['Set Nr.','상황'],as_index=False).size()

# %%
not_fixed_dial = dial_count[dial_count['size'] != 4]
# %%
not_fixed_dial.to_excel('unfixed_dialogue.xlsx')
# %%
# %%
dial_count = df.groupby(['상황'],as_index=False).size()
dial_count = dial_count.sort_values(by='size', ascending=False)
# %%
import json
with open('../data_processing/situation_label.json') as fp:
    data = json.load(fp)
# %%
data.keys()
# %%
from pathlib import Path
import json
from dataclasses import dataclass
from typing import List
from pprint import pprint


@dataclass
class Loader:
    path : str

    def __post_init__(self):
        self.name = Path(self.path).stem
        self.path = Path(self.path)
        with self.path.open() as fp:
            self._data = json.load(fp)

    @property
    def train(self):
        return self._data['train']

    @property
    def valid(self):
        return self._data['valid']

    @property
    def dataset(self):
        return self._data['train'] + self._data['valid']

@dataclass
class Analysis:
    '''
    To get data statics of SITUATION CHAT
        - Dialogues
        - Average Turns
        - Utterances
        - word count (sentence length)
    Args:
        - dataset_path: str
    '''
    dataset: List[dict]

    def __post_init__(self):
        self.history = self.get_history()


    def get_history(self):
        self._history = []
        for dialog in self.dataset:
            gold_history = []
            last_utt = dialog['utterances'][-1]
            gold_history = last_utt['history'].copy()
            gold_history.append(last_utt['candidates'][-1])
            self._history.append(gold_history)
        return self._history

    @property
    def num_of_dialogue(self) -> str:
        '''Get number of persona'''
        return f"Dialogue: {len(self.history)}"

    @property
    def num_of_utterance(self) -> str:
        '''Get number of utterance'''
        num_of_utt = sum([len(dialog) for dialog in self.history])
        return f"Utterance: {num_of_utt}"

    @property
    def average_turns(self) -> str:
        '''Get average turns'''
        average_turns = sum([len(dialog) for dialog in self.history]) / len(self.history)
        return f"Average Turns: {average_turns}"

    @property
    def example(self):
        return sum([len(dialog['utterances']) for dialog in self.dataset])


    def count_words(self) -> int:
        '''Get number of words in utterance'''
        words = 0
        for dialogs in self.history:
            for dialog in dialogs:
                words += len(dialog.split())
        return words

    @property
    def average_words(self) -> str:
        '''Get average words'''
        num_of_utt = sum([len(dialog) for dialog in self.history])
        average_words = self.count_words() / num_of_utt
        return f"Average Words: {average_words}"

#%%
situation_chat = Loader('../data/situationchat_original.json')
persona_chat = Loader('../data/personachat_self_original.json')
#%%
datasets = [situation_chat, persona_chat]
print("TRAIN: ")
for dataset in datasets:
    analysis = Analysis(dataset.train)
    print(f"{dataset.name}")
    print(f"num_of_dialogue : {analysis.num_of_dialogue}",
          f"num_of_utterance : {analysis.num_of_utterance}",
          f"average_turns : {analysis.average_turns}",
          f"example : {analysis.example}",
          f"average_words : {analysis.average_words}",
          sep='\n')
    print('-'*20)

print("VALID: ")
for dataset in datasets:
    analysis = Analysis(dataset.valid)
    print(f"{dataset.name}")
    print(f"num_of_dialogue : {analysis.num_of_dialogue}",
          f"num_of_utterance : {analysis.num_of_utterance}",
          f"average_turns : {analysis.average_turns}",
          f"example : {analysis.example}",
          f"average_words : {analysis.average_words}",
          sep='\n')
    print('-'*20)

#%%
import json
SITUATION_CHAT = '../data/situationchat_original.json'
PERSONA_CHAT = '../data/personachat_original.json'

with open(f'{PERSONA_CHAT}') as fp:
    data = json.load(fp)

# %%
train = data['train']
# %%
entry_count = len(train) * 4
print(f"Entry count: {entry_count}")
# %%
len(train[0]['utterances'])
# %%

entry_cnt = 0
for entry in train:
    turn_cnt = len(entry['utterances'])
    entry_cnt += turn_cnt

print(f"Entry count: {entry_cnt}")



# %%
