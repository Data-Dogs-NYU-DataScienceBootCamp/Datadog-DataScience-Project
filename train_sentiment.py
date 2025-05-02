import argparse
import pickle
from pathlib import Path
from typing import Dict

import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
)

LABEL_MAP = {"negative": 0, "neutral": 1, "positive": 2}
ID2LABEL = {v: k for k, v in LABEL_MAP.items()}


class SentimentClassifier:
    """Lightweight wrapper for inference & pickling."""

    def __init__(self, model, tokenizer):
        self.model = model.eval()
        self.tokenizer = tokenizer

    @torch.no_grad()
    def predict(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        label_id = int(self.model(**inputs).logits.argmax(-1))
        return ID2LABEL[label_id]


# ── data helpers ────────────────────────────────────────────────

def load_dataset(csv_path: str, tokenizer):
    df = (
        pd.read_csv(csv_path)
        .dropna(subset=["Text", "Sentiment"])
        .assign(label=lambda d: d["Sentiment"].str.lower().map(LABEL_MAP))
    )

    for k, v in ID2LABEL.items():
        print(f"{v:<8}: {(df['label']==k).sum()} samples")

    ds = Dataset.from_pandas(df[["Text", "label"]])

    def _tok(batch):
        return tokenizer(batch["Text"], truncation=True, padding="max_length", max_length=128)

    return ds.map(_tok, batched=True).train_test_split(test_size=0.1, seed=42)


# ── metrics ────────────────────────────────────────────────────

def compute_metrics(pred):
    y_pred = pred.predictions.argmax(-1)
    y_true = pred.label_ids
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


# ── safe TrainingArguments constructor ─────────────────────────

def make_training_args(base: Dict):
   
    try:
        return TrainingArguments(**base)
    except TypeError as e:
        msg = str(e)
        if "got an unexpected keyword argument" in msg:
            bad_key = msg.split("argument '")[1].split("'")[0]
            print(f"⚠️  Removing unsupported arg '{bad_key}' for this transformers version.")
            base.pop(bad_key, None)
            # cascade removals that depend on evaluation_strategy
            if bad_key == "evaluation_strategy":
                base.pop("load_best_model_at_end", None)
                base.pop("metric_for_best_model", None)
            return make_training_args(base)
        raise  # re‑raise other errors


# ── training routine ───────────────────────────────────────────

def train(csv_path: str, out_pkl: str, ckpt_dir: str):
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    ds = load_dataset(csv_path, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(LABEL_MAP),
        id2label=ID2LABEL,
        label2id=LABEL_MAP, 
    )

    args_dict = dict(
        output_dir=ckpt_dir,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        weight_decay=0.01,
        logging_dir=f"{ckpt_dir}/logs",
        report_to="none",
        evaluation_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
    )

    training_args = make_training_args(args_dict)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["test"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()

    results = trainer.evaluate()
    print("\nEval metrics:")
    for k, v in results.items():
        print(f"{k.replace('eval_', ''):<10}: {v:.4f}")

    preds = trainer.predict(ds["test"]).predictions.argmax(-1)
    print("\nClassification report:\n", classification_report(ds["test"]["label"], preds, target_names=[ID2LABEL[i] for i in range(3)]))

    Path(out_pkl).parent.mkdir(parents=True, exist_ok=True)
    with open(out_pkl, "wb") as f:
        pickle.dump(SentimentClassifier(model, tokenizer), f)
    print(f"\nModel saved → {out_pkl}")


# ── CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    pr = argparse.ArgumentParser()
    pr.add_argument("--csv", default="models/sentimentdataset.csv", help="Path to sentiment CSV file")
    pr.add_argument("--out", default="models/sentiment_model.pkl", help="Pickle output path")
    pr.add_argument("--ckpt", default="model_checkpoints", help="Checkpoint directory")
    args = pr.parse_args()

    train(args.csv, args.out, args.ckpt)
