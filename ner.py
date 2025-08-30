from typing import Iterable, List, Tuple
import pandas as pd
import numpy as np
from common import Detection
import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# ---------------------------
# spaCy loader + detection
# ---------------------------

def load_spacy(model_name: str = "en_core_web_sm"):
    """Load a spaCy NER model."""
    return spacy.load(model_name)


def detect_spacy(
        df: pd.DataFrame,
        text_columns: List[str],
        model=None,
        labels: Iterable[str] = ("PERSON", "ORG", "GPE")
) -> List[Detection]:
    """Detect entities using a spaCy model."""
    if model is None:
        model = load_spacy()

    detections: List[Detection] = []
    wanted = set(labels)

    for col in text_columns:
        for idx, val in df[col].items():
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            text = str(val).strip()
            if not text:
                continue

            doc = model(text)
            for ent in doc.ents:
                if ent.label_ in wanted:
                    detections.append(
                        Detection(
                            row=idx,
                            col=col,
                            start=ent.start_char,
                            end=ent.end_char,
                            value=ent.text,
                            label=ent.label_,
                        )
                    )
    return detections


# ---------------------------
# HuggingFace loader + detection
# ---------------------------

def load_hf(model_name: str = "dslim/bert-large-NER"):
    """Load a HuggingFace NER pipeline."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)
    return pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")


def detect_hf(
        df: pd.DataFrame,
        text_columns: List[str],
        model=None,
        labels: Iterable[str] = ("PER", "ORG", "LOC")
) -> List[Detection]:
    """Detect entities using a HuggingFace NER model."""
    if model is None:
        model = load_hf()

    detections: List[Detection] = []
    wanted = set(labels)

    for col in text_columns:
        for idx, val in df[col].items():
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            text = str(val).strip()
            if not text:
                continue

            ents = model(text)
            for ent in ents:
                if ent["entity_group"] in wanted:
                    detections.append(
                        Detection(
                            row=idx,
                            col=col,
                            start=ent["start"],
                            end=ent["end"],
                            value=text[ent["start"]:ent["end"]],
                            label=ent["entity_group"],
                        )
                    )
    return detections
