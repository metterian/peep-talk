
<h1 align="center">
  <br>
  <a href="https://pf.kakao.com/_FlDxgs"><img src="https://i.loli.net/2021/10/31/D8Kng1xrlOhHFqL.png" alt="PEEP-Talk Logo"></a>
</h1>

<h4 align="center">PEEP-Talk: A Situational Dialogue-Based English Education Platform</h4>

<p align="center">
    <img alt="python-3.7.7" src="https://img.shields.io/badge/python-3.7.7-blue"/>
    <img alt="huggingface-3.1.0" src="https://img.shields.io/badge/huggingface-3.1.0-yellow"/>
    <img alt="pytorch-1.7.0" src="https://img.shields.io/badge/pytorch-1.7.0-blueviolet"/>
    <img alt="GitHub" src="https://img.shields.io/github/license/metterian/redbttn-seoul-studio"/>
</p>


> PEEP-Talk is an educational platform with a deep learning-based persona conversation system and a feedback function for correcting English grammar. In addition, unlike the existing persona conversation system, a Context Detector (CD) module that can automatically determine the flow of conversation and change the conversation topic in real time can be applied to give the user a feeling of talking to a real person.

<br/>


## Dataset

- Download testset of SITUATION-CHAT from this [link](https://raw.githubusercontent.com/metterian/peep-talk/master/data/situationchat_original_test.json)



<br/>


## Project interests

### Conversational Agent
By considering persona as a situation, English conversation learning for each situation becomes possible. To make conversational agent model mainly, we use Hugging Face's [TransferTransfo](https://github.com/huggingface/transfer-learning-conv-ai) code.

### Context Detector
This module can detect whether user speak properly in suggested situation or not. This module contains two BERT based models. Evaluate the conversation using the following two functions. Based on that score, we decide whether to change the conversation.
- **Situation Similarity**(상황 유사도): fine-tuinig the MRPC(Microsoft Research Paraphrase Corpus) dataset to detect user's context similarity in suggested situation.
- **Linguistic Acceptability**(문장 허용도): fine-tuning the CoLA(The Corpus of Linguistic Acceptability) dataset to detect user's input is acceptable in human conversation.

### Grammar Error Correction
To give grammar feedback to english learner, We use GEC(Grammar Error Correction) as REST API.
- [paper](https://ieeexplore.ieee.org/document/9102992)

## Folder Structure
    .
    ├── train.py                # Train model
    ├── app.py                  # REST API code
    ├── run.py                  # running PEEP-Talk
    ├── requirements.txt
    ├── LICENSE
    └── README.md





## Run
to interact with PEEP-talk :
```
python interact.py
```
to REST API server:
```
python app.py
```

to use Streamlit
```
streamlit run web.py
```


## Demo
- [Web](http://peeptalk.us)
- [Video](https://www.youtube.com/watch?v=PXlIEOi54wY)



## License
The MIT License
