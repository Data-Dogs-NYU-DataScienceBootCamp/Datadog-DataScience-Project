import json, pathlib, pandas as pd
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from collections import Counter
import nltk, ssl
ssl._create_default_https_context = ssl._create_unverified_context  # macOS fix
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords

# ── load & basic clean ────────────────────────────────────────────
df = (
    pd.read_csv("data/sentimentdataset.csv")
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
    # Neutral ─────────────────────────────────────────
    "neutral":"Neutral","confusion":"Neutral","indifference":"Neutral",
    "numbness":"Neutral","nostalgia":"Neutral","ambivalence":"Neutral",
    "pensive":"Neutral",

    # Positive ───────────────────────────────────────
    "positive":"Positive","happiness":"Positive","joy":"Positive","love":"Positive",
    "amusement":"Positive","enjoyment":"Positive","admiration":"Positive",
    "affection":"Positive","awe":"Positive","acceptance":"Positive","adoration":"Positive",
    "anticipation":"Positive","calmness":"Positive","excitement":"Positive",
    "elation":"Positive","euphoria":"Positive","contentment":"Positive",
    "serenity":"Positive","gratitude":"Positive","hope":"Positive","empowerment":"Positive",
    "compassion":"Positive","tenderness":"Positive","arousal":"Positive",
    "enthusiasm":"Positive","fulfillment":"Positive","reverence":"Positive",
    "kind":"Positive","pride":"Positive","zest":"Positive","hopeful":"Positive",
    "grateful":"Positive","empathetic":"Positive","compassionate":"Positive",
    "playful":"Positive","free-spirited":"Positive","inspired":"Positive",
    "confident":"Positive","overjoyed":"Positive","inspiration":"Positive",
    "motivation":"Positive","joyfulreunion":"Positive","satisfaction":"Positive",
    "blessed":"Positive","appreciation":"Positive","confidence":"Positive",
    "accomplishment":"Positive","wonderment":"Positive","optimism":"Positive",
    "enchantment":"Positive","intrigue":"Positive","playfuljoy":"Positive",
    "mindfulness":"Positive","dreamchaser":"Positive","elegance":"Positive",
    "whimsy":"Positive","thrill":"Positive","harmony":"Positive","creativity":"Positive",
    "radiance":"Positive","wonder":"Positive","rejuvenation":"Positive",
    "coziness":"Positive","adventure":"Positive","melodic":"Positive",
    "festivejoy":"Positive","innerjourney":"Positive","freedom":"Positive",
    "dazzle":"Positive","adrenaline":"Positive","artisticburst":"Positive",
    "culinaryodyssey":"Positive","spark":"Positive","marvel":"Positive",
    "positivity":"Positive","kindness":"Positive","friendship":"Positive",
    "success":"Positive","exploration":"Positive","amazement":"Positive",
    "romance":"Positive","captivation":"Positive","tranquility":"Positive",
    "grandeur":"Positive","emotion":"Positive","energy":"Positive",
    "celebration":"Positive","charm":"Positive","ecstasy":"Positive",
    "colorful":"Positive","hypnotic":"Positive","connection":"Positive",
    "iconic":"Positive","journey":"Positive","engagement":"Positive",
    "touched":"Positive","triumph":"Positive","heartwarming":"Positive",
    "breakthrough":"Positive","joy in baking":"Positive","imagination":"Positive",
    "vibrancy":"Positive","mesmerizing":"Positive","culinary adventure":"Positive",
    "winter magic":"Positive","thrilling journey":"Positive","nature's beauty":"Positive",
    "celestial wonder":"Positive","creative inspiration":"Positive",
    "runway creativity":"Positive","ocean's freedom":"Positive",
    "whispers of the past":"Positive","relief":"Positive","happy":"Positive",

    # Negative ───────────────────────────────────────
    "negative":"Negative","anger":"Negative","fear":"Negative","sadness":"Negative",
    "disgust":"Negative","disappointed":"Negative","bitter":"Negative","shame":"Negative",
    "despair":"Negative","grief":"Negative","loneliness":"Negative","jealousy":"Negative",
    "resentment":"Negative","frustration":"Negative","boredom":"Negative","anxiety":"Negative",
    "intimidation":"Negative","helplessness":"Negative","envy":"Negative","regret":"Negative",
    "bitterness":"Negative","yearning":"Negative","fearful":"Negative",
    "apprehensive":"Negative","overwhelmed":"Negative","jealous":"Negative",
    "devastated":"Negative","frustrated":"Negative","envious":"Negative",
    "dismissive":"Negative","bittersweet":"Negative","sad":"Negative","hate":"Negative",
    "bad":"Negative","embarrassed":"Negative","mischievous":"Negative","lostlove":"Negative",
    "betrayal":"Negative","suffering":"Negative","emotionalstorm":"Negative",
    "isolation":"Negative","disappointment":"Negative","heartbreak":"Negative",
    "sorrow":"Negative","darkness":"Negative","desperation":"Negative","ruins":"Negative",
    "desolation":"Negative","loss":"Negative","heartache":"Negative","obstacle":"Negative",
    "pressure":"Negative","miscalculation":"Negative","exhaustion":"Negative",
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

print("✔ JSON files rebuilt in static/data/")

pathlib.Path("static/data").mkdir(parents=True, exist_ok=True)
pathlib.Path("models").mkdir(parents=True, exist_ok=True)         

# ── save cleaned CSV for training ────────────────────────────────
df.to_csv("models/sentimentdataset.csv", index=False)     