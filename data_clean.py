import json, pathlib, pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import nltk, ssl
ssl._create_default_https_context = ssl._create_unverified_context  # macOS fix
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords

<<<<<<< HEAD
df = pd.read_csv("mosdel/sentimentdataset.csv")


df = (df
=======
# ── load & basic clean ────────────────────────────────────────────
df = (
    pd.read_csv("data/sentimentdataset.csv")
>>>>>>> 392f590a3c7c429787c87cfa8dd715ff16a8964b
      .drop_duplicates()
      .dropna(subset=["Text"])
      .rename(columns=str.title)
)

df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Retweets"]  = df["Retweets"].astype(int)
df["Likes"]     = df["Likes"].astype(int)
df["Platform"] = df["Platform"].astype(str).str.strip().str.title()


# ── sentiment mapping to 3 buckets ───────────────────────────────
mapping = {
    "neutral":  "Neutral",  "confusion": "Neutral",  "indifference": "Neutral",
    "numbness": "Neutral",  "nostalgia": "Neutral",  "ambivalence":  "Neutral",
    "pensive":  "Neutral",
    "positive": "Positive", "happiness": "Positive", "joy":    "Positive",
    "love":     "Positive", "amusement": "Positive", "enjoyment":"Positive",
    "admiration":"Positive","affection":"Positive",  "awe":    "Positive",
    "negative": "Negative", "anger":     "Negative", "sadness":"Negative",
    "fear":     "Negative", "hate":      "Negative", "disgust":"Negative"
}

df["Sentiment"] = (
    df["Sentiment"].astype(str)
      .str.strip().str.lower()
      .map(mapping)
      .fillna("Neutral")
)

# ── basic NLP tokens (kept for future use) ───────────────────────
tok = RegexpTokenizer(r"\w+")
stops = set(stopwords.words("english"))
df["Tokens"] = (
    df["Text"].str.lower()
      .apply(tok.tokenize)
      .apply(lambda t: [w for w in t if w not in stops])
)

# ── make sure folders exist ──────────────────────────────────────
pathlib.Path("static/data").mkdir(parents=True, exist_ok=True)

# ── bar-chart distribution ───────────────────────────────────
vc = df["Sentiment"].value_counts()

distribution = {
    "labels": vc.index.tolist(),
    "datasets": [{
        "label": "Sentiment Distribution",
        "backgroundColor": ["#4caf50", "#ffc107", "#f44336"],
        "data": vc.tolist()
    }]
}
json.dump(distribution, open("static/data/distribution.json", "w"), indent=2)

# ── scatter (retweets × likes) ────────────────────────────────
scatter = (
    df[["Retweets", "Likes", "Sentiment"]]
      .rename(columns={"Retweets":"retweets","Likes":"likes","Sentiment":"sentiment"})
)
scatter.to_json("static/data/scatter.json", orient="records", indent=2)

# ── daily time-series counts ─────────────────────────────────
ts = (
    df.resample("D", on="Timestamp")["Sentiment"]
      .value_counts().unstack(fill_value=0)
)
ts.index = ts.index.strftime("%Y-%m-%d")

timeseries = {
    "dates": ts.index.tolist(),
    "series": {col: ts[col].tolist() for col in ts.columns}
}
json.dump(timeseries, open("static/data/timeseries.json", "w"), indent=2)

# ── engagement heat-map (median likes/retweets) ──────────────
df["dow"]  = df["Timestamp"].dt.day_name()
df["hour"] = df["Timestamp"].dt.hour.astype(int)

heat = (
    df.groupby(["dow","hour"])[["Likes","Retweets"]]
      .median().reset_index()
      .rename(columns={"Likes":"likes","Retweets":"retweets"})
)
heat.to_json("static/data/heatmap.json", orient="records", indent=2)


# ---- hourly engagement -----------------------------------------
hour_avg = (
    df.groupby('Hour')[['Likes', 'Retweets']]
      .mean()
      .reset_index()
      .round(1)
)
hour_avg.to_json("static/data/hourly.json", orient="records", indent=2)

# --------- platform split -----------------------
plat = df['Platform'].value_counts()
platform_json = {
    "labels": plat.index.tolist(),
    "data":   plat.tolist(),
    "colors": ["#1DA1F2", "#E4405F", "#5865F2", "#ff9800", "#9c27b0"]  
}
json.dump(platform_json, open("static/data/platform.json", "w"), indent=2)


print("✔ JSON files rebuilt in static/data/")