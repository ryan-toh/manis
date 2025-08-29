from typing import Iterable, List, Optional
import pandas as pd
import numpy as np
from common import Detection
import spacy

def load_ner(model_name: str = "en_core_web_sm"):
    """
    Load and return the NER model (spaCy pipeline or similar).
    Input:  model_name -> spaCy model name
    Output: model object (opaque to callers)
    """
    return spacy.load(model_name)


def detect_ner(
    df: pd.DataFrame,
    text_columns: List[str],
    model=None,
    labels: Iterable[str] = ("PERSON", "ORG", "GPE")
) -> List[Detection]:
    """
    Run NER over the given text columns and collect PERSON/ORG/LOCATION (GPE).
    Input:
        df              -> pandas DataFrame
        text_columns    -> which columns to scan (strings)
        model           -> from load_ner(); if None, load inside
        labels          -> which entity labels to keep
    Output:
        list of Detection objects
    """

    # 1) Load model if not provided
    if model is None:
        # Local import to avoid circulars if load_ner is in same module
        model = load_ner()

    # 2) Validate columns
    missing = [c for c in text_columns if c not in df.columns]
    if missing:
        raise ValueError(f"detect_ner: columns not found in DataFrame: {missing}")

    # 3) Prepare (row_index, column_name, text) triples, skipping NaN/empty
    tasks: List[Tuple[int, str, str]] = []
    for col in text_columns:
        series = df[col]
        # Ensure string-ish; skip NaN/None; strip empties
        for idx, val in series.items():
            if val is None or (isinstance(val, float) and np.isnan(val)):
                continue
            text = str(val).strip()
            if not text:
                continue
            tasks.append((idx, col, text))

    # Nothing to do
    if not tasks:
        return []

    # 4) Run spaCy in batch for speed
    #    We keep (idx, col) alongside each text so we can map results back
    detections: List[Detection] = []
    wanted = set(labels)

    # pipe only accepts the texts; keep parallel metadata list
    texts = [t[2] for t in tasks]
    metas = [(t[0], t[1]) for t in tasks]

    # Choose a sensible batch size; spaCy will also auto-chunk
    for (doc, (row_idx, col)) in zip(model.pipe(texts, disable=["tagger", "lemmatizer", "attribute_ruler"]), metas):
        for ent in getattr(doc, "ents", []):
            if ent.label_ in wanted and ent.text.strip():
                # Construct a Detection. If your Detection has different field names,
                # adapt here accordingly.
                detections.append(
                    Detection(
                        row=row_idx,
                        col=col,
                        start=ent.start_char,
                        end=ent.end_char,
                        value=ent.text,
                        label=ent.label_,
                    )
                )

    return detections

# Dummy dataset with examples that should trigger each label type
df = pd.DataFrame({
    "notes": [
        "Barack Obama visited New York.",             # PERSON + GPE
        "Google acquired a startup in Paris.",        # ORG + GPE
        "Contact me at alice@example.com",            # EMAIL
        "Call me at +1-202-555-0147",                 # PHONE
        "My credit card number is 4111-1111-1111-1111", # CREDIT_CARD
        "Server is at 192.168.0.1",                   # IP
        "No sensitive data here."                     # Nothing
    ],
    "comments": [
        "Meeting with Microsoft in London",           # ORG + GPE
        "Elon Musk gave a talk in California",        # PERSON + LOCATION
        "Support email: support@company.org",         # EMAIL
        "Phone: (555) 123-4567",                      # PHONE
        "Visa card: 5555-4444-3333-2222",             # CREDIT_CARD
        "API endpoint at 10.0.0.42",                  # IP
        "Plain text comment"                          # Nothing
    ]
})


# # Run detection
# nlp = load_ner()
# detections = detect_ner(
#     df=df,
#     text_columns=["notes", "comments"],
#     model=nlp,
#     labels=("PERSON", "ORG", "GPE")  # for NER part
# )

# # Show results
# for d in detections:
#     print(d)

