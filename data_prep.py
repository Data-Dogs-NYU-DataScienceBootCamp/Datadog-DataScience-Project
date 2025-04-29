import json, pandas as pd, pathlib, sys

df = pd.read_csv("data/sentimentdataset.csv")

#sentiment
candidates = ["sentiment", "label", "polarity", "target", "category"]
sent_col = next((c for c in candidates if c in df.columns), None)
if sent_col is None:                      # fall-back: first non-numeric column
    sent_col = df.select_dtypes(include="object").columns[0]
    sys.stderr.write(
        f"[info] No standard header found; using column “{sent_col}”.\n"
    )

vc = df[sent_col].value_counts()

pathlib.Path("static/data").mkdir(parents=True, exist_ok=True)

json.dump(
    {"labels": vc.index.tolist(), "counts": vc.tolist()},
    open("static/data/distribution.json", "w")
)

print("[✓] distribution.json written to static/data/")
