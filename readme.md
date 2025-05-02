# Social Media Sentiment Analysis

A small Flask app that:
- Cleans and preprocesses a sentiment dataset  
- Trains an LSTM next‐word model  
- Fine‑tunes a BERT sentiment classifier  
- Exposes a simple REST API for caption generation and sentiment analysis

---

## 1. Prerequisites

- Python 3.8+  
- Git

---

## 2. Install dependencies

```bash
pip install -r requirements.txt

## 3. Order of Execution
python data_clean.py
python train_lstm.py
python train_sentiment.py
python data_prep.py

## 4. Start the app
python app.py
