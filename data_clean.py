
import json, pathlib, pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import nltk, ssl
ssl._create_default_https_context = ssl._create_unverified_context  # macOS fix
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords

df = pd.read_csv("data/sentimentdataset.csv")


df = (df
      .drop_duplicates()
      .dropna(subset=["Text"])          
      .rename(columns=str.title)         
     )

df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Retweets"]  = df["Retweets"].astype(int)
df["Likes"]     = df["Likes"].astype(int)

# ── sentiment 3-bucket mapping 
mapping = {
    # Neutral
    "neutral":"Neutral", "confusion":"Neutral", "indifference":"Neutral",
    "numbness":"Neutral", "nostalgia":"Neutral", "ambivalence":"Neutral",
    "pensive":"Neutral",
    # Positive
    "positive":"Positive","happiness":"Positive","joy":"Positive",
    "love":"Positive","amusement":"Positive","enjoyment":"Positive",
    "admiration":"Positive","affection":"Positive","awe":"Positive",
    # Negative
    "negative":"Negative","anger":"Negative","sadness":"Negative",
    "fear":"Negative","hate":"Negative","disgust":"Negative"
}
df["Sentiment"] = df["Sentiment"].str.lower().map(mapping).fillna("Neutral")


tokenizer = RegexpTokenizer(r"\w+")
stops = set(stopwords.words("english"))
df["Tokens"] = (df["Text"]
                .str.lower()
                .apply(tokenizer.tokenize)
                .apply(lambda toks:[t for t in toks if t not in stops]))


pathlib.Path("data").mkdir(exist_ok=True)
df.to_csv("data/sentimentdataset.csv", index=False)

# sentiment distribution for bar-chart
vc = df["Sentiment"].value_counts()
json.dump({"labels": vc.index.tolist(), "counts": vc.tolist()},
          open("static/data/distribution.json","w"))

#  scatter: retweets vs likes, coloured by sentiment 
json.dump(df[["Retweets","Likes","Sentiment"]].to_dict(orient="records"),
          open("static/data/scatter.json","w"))

# time-series: daily sentiment counts 
# ── 3. time-series: daily sentiment counts ───────────────────────
ts = (df.resample("D", on="Timestamp")["Sentiment"]
         .value_counts()
         .unstack(fill_value=0))

# stringify the index so JSON accepts it
ts.index = ts.index.strftime("%Y-%m-%d")

json.dump(
    {
        "dates": ts.index.tolist(),
        "series": {sent: ts[sent].tolist() for sent in ts.columns}
    },
    open("static/data/timeseries.json", "w")
)


#day-of-week × hour 
df["DOW"]  = df["Timestamp"].dt.day_name()
df["Hour"] = df["Timestamp"].dt.hour
heat = (df.groupby(["DOW","Hour"])[["Likes","Retweets"]]
          .median()
          .reset_index())
json.dump(heat.to_dict(orient="records"),
          open("static/data/heatmap.json","w"))

print("✔ Data cleaned & JSON files written to static/data/")
