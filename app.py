
import os
os.environ["TRANSFORMERS_NO_TF_IMPORT"] = "1"

import json, pickle
from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import keras                                
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import random

STARTERS = ["This is", "Feeling", "Discover", "Experience", "Embrace", "Unleash", "Dive into"]



# ── LSTM next-word model
lstm = keras.saving.load_model("models/lstm_nextword.keras")
tok = pickle.load(open("models/tokenizer.pkl", "rb"))
max_len = lstm.input_shape[1]

def next_words(seed: str, n: int = 100, temperature: float = 1.0) -> str:
    """Generate next `n` words after `seed` using temperature sampling."""
    for _ in range(n):
        seq = pad_sequences([tok.texts_to_sequences([seed])[0]], maxlen=max_len-1)
        preds = lstm.predict(seq, verbose=0)[0]

        # apply temperature
        preds = np.log(preds + 1e-8) / temperature
        preds = np.exp(preds) / np.sum(np.exp(preds))

        next_id = np.random.choice(len(preds), p=preds)
        next_word = tok.index_word.get(next_id, "")

        if not next_word:  # unknown word, skip
            continue
        seed += " " + next_word
    return seed


# ── BERT sentiment pipeline (PyTorch) 
sentiment_pipe = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    framework="pt"                 
)

def predict_sentiment(text: str):
    out = sentiment_pipe(text, truncation=True)[0]
    raw_label, score = out["label"], out["score"]

    # map RoBERTa’s LABEL_0/1/2 → human-readable
    pretty = {"LABEL_0": "negative",
              "LABEL_1": "neutral",
              "LABEL_2": "positive"}.get(raw_label, raw_label)

    mood = {"positive": "😊", "neutral": "😐", "negative": "😞"}.get(pretty, "🤔")
    return pretty, score, mood


app = Flask(__name__)

@app.route("/")
def root():                       
    return render_template("overview.html")

@app.route("/overview")
def overview():
    return render_template("overview.html")

@app.route("/charts")
def charts():
    return render_template("charts.html")

@app.route("/sentiment")
def sentiment():
    return render_template("sentiment.html")  

@app.route("/api/caption", methods=["POST"])
def api_caption():
    data = request.get_json(silent=True) or {}
    keywords = data.get("keywords", "")

    # Select a random starter phrase
    starter_seed = random.choice(STARTERS)

    # Generate a caption starting with the selected starter
    caption = next_words(starter_seed, n=20, temperature=0.9)

    # Clean and format the caption
    caption = caption.capitalize().strip()

    # Append the original keywords at the end
    final_caption = f"{caption} {keywords}"

    return jsonify({"caption": final_caption})




# ── REST API endpoints ────────────────────────────────────────────
@app.route("/api/sentiment", methods=["POST"])
def api_sentiment():
   
    data = request.get_json(silent=True) or {}
    text  = data.get("text", "")
    label, score, mood = predict_sentiment(text)
    return jsonify({"label": label, "score": score, "emoji": mood})


@app.route("/api/generate", methods=["POST"])
def api_generate():
   
    data = request.get_json(silent=True) or {}
    seed = data.get("seed", "")
    return jsonify({"generated": next_words(seed)})



# ── main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)