
<h1 align="center">
  <br>
  <a href="https://pf.kakao.com/_FlDxgs"><img src="https://i.loli.net/2021/10/31/D8Kng1xrlOhHFqL.png" alt="PEEP-Talk Logo"></a>
</h1>

<h4 align="center">PEEP-Talk: Deep Learning-based English Education Platform for Personalized Foreign Language Learning</h4>
<p align="center">Human-inspired AI, Korea University</p>

<p align="center">
    <img alt="python-3.7.7" src="https://img.shields.io/badge/python-3.7.7-blue"/>
    <img alt="django-2.2.5" src="https://img.shields.io/badge/KakaoTalk-offline-yellow"/>
    <img alt="chromedriver-79.0.3945" src="https://img.shields.io/badge/chromedriver-79.0.3945-blueviolet"/>
    <img alt="GitHub" src="https://img.shields.io/github/license/metterian/redbttn-seoul-studio"/>
</p>


> PEEP-Talk is an educational platform with a deep learning-based persona conversation system and a feedback function for correcting English grammar. In addition, unlike the existing persona conversation system, a Context Detector (CD) module that can automatically determine the flow of conversation and change the conversation topic in real time can be applied to give the user a feeling of talking to a real person.

> The source code is open so that you can download the source code and set it up with ease if you would like to have your own exclusive environment, and this platform is deployed by Kakao i Open Builder.

## Screenshots

screenshot1             |  screenshot2
:-------------------------:|:-------------------------:
![](https://i.loli.net/2021/10/31/nYtvxABGIHQsDL2.png)  |  ![](https://i.loli.net/2021/10/31/4BHTGFmatUACcP2.png)

<br/>


## Project interests

### Conversational Agent
By considering persona as a situation, English conversation learning for each situation becomes possible. To make conversational agent model mainly, we use Hugging Face's [TransferTransfo](https://github.com/huggingface/transfer-learning-conv-ai) code.

### Context Detector
This module can detect whether user speak properly in suggested situation or not. This module contains two BERT based models. Evaluate the conversation using the following two functions. Based on that score, we decide whether to change the conversation.
- **Context Similarity**(상황 유사도): fine-tuinig the MRPC(Microsoft Research Paraphrase Corpus) dataset to detect user's context similarity in suggested situation.
- **Linguistic Acceptability**(문장 허용도): fine-tuning the CoLA(The Corpus of Linguistic Acceptability) dataset to detect user's input is acceptable in human conversation.

### Grammar Error Correction
To give grammar feedback to english learner, We use GEC(Grammar Error Correction) as REST API.
- [paper](https://ieeexplore.ieee.org/document/9102992)

## Folder Structure
    .
    ├── data_preprocessing      # data preprocess
    ├── alf_test.py             # experiment for context detector
    ├── app.py                  # REST API code
    ├── kakao.py                # REST API code for Kakao Channel
    ├── run.py                  # running PEEP-Talk
    ├── requirements.txt
    ├── LICENSE
    └── README.md



## Metric
### Experiment Setting

| Model   | Epoch | Batch size | Learning rate | Sequence length |
|---------|:-----:|:----------:|:-------------:|:---------------:|
| BERT    |   5   |     16     |     2e-05     |       256       |
| ALBERT  |   5   |     32     |     2e-05     |       128       |
| RoBERTa |   5   |     16     |     3e-05     |       256       |
| XLNet   |   5   |     32     |     5e-05     |       256       |


### Context Detecotr Metric Result
| Model   |  MRPC |
|---------|:-----:|
| BERT    | 0.876 |
| ALBERT  | 0.884 |
| RoBERTa | 0.923 |
| XLNet   | 0.928 |


### CoLA Result
|         |    CoLA    |       |
|---------|:----------:|-------|
| Model   | Validation |  Test |
| BERT    |    0.812   | 0.820 |
| ALBERT  |    0.728   | 0.736 |
| RoBERTa |    0.739   | 0.755 |
| XLNet   |    0.851   | 0.870 |



## Run
to interact with PEEP-talk :
```
python run.py
```
to kakao server:
```
python kakao.py
```


## Demo Video
- [PC Version](https://youtu.be/Mma23gbCMAU)


## Award
This project got **Best Paper Award** from HCTL(Human & Cognitive Language Technology: 한글 및 한국어 정보처리 학술대회)

## Citation
```bibtex
@inproceedings{lee2021peep,
  title={PEEP-Talk: Deep Learning-based English Education Platform for Personalized Foreign Language Learning},
  author={Lee, SeungJun and Jang, Yoonna and Park, Chanjun and Kim, Minwoo and Yahya, Bernardo N and Lim, Heuiseok},
  booktitle={Annual Conference on Human and Language Technology},
  pages={293--299},
  year={2021},
  organization={Human and Language Technology}
}
```

## License
The MIT License
