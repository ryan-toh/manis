import math
import numpy as np
import pandas as pd
import pytest

# Adjust these imports to your package structure
from ner import load_ner, detect_ner
from common import Detection  # your dataclass: row, col, start, end, label, value


# ---------- Fixtures ----------

@pytest.fixture(scope="session")
def nlp():
    # Ensure you've installed a model, e.g.:
    #   python -m spacy download en_core_web_sm
    return load_ner("en_core_web_sm")


@pytest.fixture
def toy_df():
    return pd.DataFrame({
        "title": [
            "Apple hires Sam Altman in San Francisco",
            "Barack Obama visited Berlin",
            None,
            "No entities here"
        ],
        "body": [
            "Google met with OpenAI leaders in New York on Monday.",
            "Microsoft acquired a startup in Paris.",
            "Paris is lovely in springtime.",
            ""
        ],
    })


# ---------- Helpers ----------

def detections_to_df(dets: list[Detection]) -> pd.DataFrame:
    """Convert detections into a DataFrame for easier assertions."""
    return pd.DataFrame([{
        "row": d.row,
        "col": d.col,
        "start": d.start,
        "end": d.end,
        "label": d.label,
        "value": d.value,
    } for d in dets])


def assert_offsets_match_source(df: pd.DataFrame, dets: list[Detection]) -> None:
    """Verify that each Detection's (start:end) slice matches its value."""
    for d in dets:
        assert d.col in df.columns, f"Unknown column in detection: {d.col}"
        cell = df.loc[d.row, d.col]
        # Skip checks for None/NaN (shouldn't occur if your function skips them)
        if cell is None or (isinstance(cell, float) and math.isnan(cell)):
            continue
        text = str(cell)
        assert 0 <= d.start <= d.end <= len(text), (
            f"Offsets out of range for row={d.row}, col={d.col}, "
            f"start={d.start}, end={d.end}, len={len(text)}"
        )
        assert text[d.start:d.end] == d.value, (
            f"Offset slice mismatch. Expected '{d.value}', "
            f"got '{text[d.start:d.end]}'"
        )


# ---------- Tests ----------

def test_happy_path_entities_present(nlp, toy_df):
    dets = detect_ner(
        df=toy_df,
        text_columns=["title", "body"],
        model=nlp,
        labels=("PERSON", "ORG", "GPE"),
    )

    # Basic shape checks
    assert isinstance(dets, list)
    assert all(isinstance(d, Detection) for d in dets)
    out = detections_to_df(dets)
    assert not out.empty

    # Columns and labels should be within the requested sets
    assert set(out["col"]).issubset({"title", "body"})
    assert set(out["label"]).issubset({"PERSON", "ORG", "GPE"})

    # Offsets must be consistent with the source text
    assert_offsets_match_source(toy_df, dets)

    # Loose content check (avoid brittleness across spaCy versions)
    candidates = {v.lower() for v in out["value"]}
    expected_any = {
        "apple", "google", "openai", "microsoft",
        "sam altman", "barack obama",
        "san francisco", "berlin", "new york", "paris"
    }
    assert candidates.intersection(expected_any), "No expected entities found at all."


def test_custom_labels_filtering_only_gpe(nlp):
    df = pd.DataFrame({"text": ["On Monday, Microsoft met in Paris and New York."]})
    dets = detect_ner(
        df=df,
        text_columns=["text"],
        model=nlp,
        labels=("GPE",),
    )
    out = detections_to_df(dets)
    # If there are detections, they must all be GPE
    assert set(out["label"]).issubset({"GPE"})
    assert_offsets_match_source(df, dets)


def test_missing_columns_raises(nlp):
    df = pd.DataFrame({"x": ["hello world"]})
    with pytest.raises(ValueError):
        detect_ner(df, ["title"], model=nlp)


def test_empty_and_nan_are_skipped(nlp):
    df = pd.DataFrame({"text": [None, "", np.nan]})
    dets = detect_ner(df, ["text"], model=nlp)
    assert dets == []  # nothing to process


def test_non_string_values_handled(nlp):
    # Non-strings should not crash; ints will be str()'d and ignored by NER
    df = pd.DataFrame({"text": ["Paris 2024", 12345, {"k": "v"}]})
    dets = detect_ner(df, ["text"], model=nlp, labels=("GPE", "ORG", "PERSON"))
    # Should run without exceptions and any detections must have valid offsets
    assert_offsets_match_source(df, dets)


def test_model_autoload_path(toy_df):
    # Ensure the internal "load if None" path works (no nlp passed)
    dets = detect_ner(
        df=toy_df,
        text_columns=["title", "body"],
        model=None,  # triggers internal load_ner()
        labels=("PERSON", "ORG", "GPE"),
    )
    # Not asserting count—just that it runs and produces valid detections (or empty)
    if dets:
        assert_offsets_match_source(toy_df, dets)
        out = detections_to_df(dets)
        assert set(out["col"]).issubset({"title", "body"})
        assert set(out["label"]).issubset({"PERSON", "ORG", "GPE"})
