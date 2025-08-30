import argparse
from typing import Optional
import pandas as pd

from ingest import read_csv, get_text_columns
from my_regex import detect_regex
from ner import load_spacy, detect_spacy, load_hf, detect_hf
from redact import apply_redactions, dedupe_overlaps


def sanitize_file(
        input_path: str,
        output_path: str,
        sample_rows: Optional[int] = None,
        use_ner: bool = True,
        use_spacy: bool = True,
        use_hf: bool = True,
        token: str = "[REDACTED]",
        intersection: bool = False
) -> dict:
    """
    End-to-end sanitization pipeline.

    Args:
        input_path: path to the input CSV file
        output_path: path to write the redacted CSV
        sample_rows: optionally restrict to first N rows
        use_ner: whether to run NER (spaCy + HF) in addition to regex
        use_spacy: run spaCy NER
        use_hf: run HuggingFace NER
        token: replacement string for redactions
        intersection: if True, only keep overlapping detections (spaCy ∩ HF)

    Returns:
        RedactionSummary dict
    """
    # 1) Load data
    df = read_csv(input_path, sample_rows)

    # 2) Regex detections
    regex_hits = detect_regex(df)

    # 3) Which columns are text?
    text_cols = get_text_columns(df)

    spacy_hits, hf_hits = [], []

    if use_ner:
        if use_spacy:
            spacy_hits = detect_spacy(
                df, text_cols,
                model=load_spacy(),
                labels=("PERSON", "ORG", "GPE", "NORP")
            )
        if use_hf:
            hf_hits = detect_hf(
                df, text_cols,
                model=load_hf(),
                labels=("PER", "ORG", "LOC")
            )

    # 4) Combine or intersect NER hits
    if intersection and spacy_hits and hf_hits:
        # keep only hits where span + label match
        spacy_set = {(d.row, d.col, d.start, d.end, d.label) for d in spacy_hits}
        hf_set = {(d.row, d.col, d.start, d.end, d.label) for d in hf_hits}
        common = spacy_set & hf_set
        ner_hits = [d for d in spacy_hits if (d.row, d.col, d.start, d.end, d.label) in common]
    else:
        ner_hits = spacy_hits + hf_hits

    # 5) Combine with regex hits + dedupe
    hits = dedupe_overlaps(regex_hits + ner_hits)

    # 6) Apply redactions
    redacted_df, summary = apply_redactions(df, hits, token)

    # 7) Write out CSV
    redacted_df.to_csv(output_path, index=False)

    # 8) Return summary
    return summary


def main():
    parser = argparse.ArgumentParser(description="Redact PII from a CSV.")
    parser.add_argument("input", help="Path to input CSV")
    parser.add_argument("output", help="Path to write redacted CSV")
    parser.add_argument("--sample", type=int, default=None, help="Limit to first N rows")
    parser.add_argument("--no-ner", action="store_true", help="Disable all NER")
    parser.add_argument("--no-spacy", action="store_true", help="Disable spaCy NER")
    parser.add_argument("--no-hf", action="store_true", help="Disable HuggingFace NER")
    parser.add_argument("--intersection", action="store_true", help="Use intersection of spaCy and HF")
    parser.add_argument("--token", default="[REDACTED]", help="Replacement token")
    args = parser.parse_args()

    summary = sanitize_file(
        input_path=args.input,
        output_path=args.output,
        sample_rows=args.sample,
        use_ner=not args.no_ner,
        use_spacy=not args.no_spacy,
        use_hf=not args.no_hf,
        token=args.token,
        intersection=args.intersection
    )

    print("Redaction summary:")
    print(summary)


if __name__ == "__main__":
    main()
