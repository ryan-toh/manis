import argparse
from typing import Optional
import pandas as pd

from ingest import read_csv, get_text_columns
from my_regex import detect_regex
from ner import load_ner, detect_ner
from redact import apply_redactions, dedupe_overlaps


def sanitize_file(
    input_path: str,
    output_path: str,
    sample_rows: Optional[int] = None,
    use_ner: bool = True,
    token: str = "[REDACTED]"
) -> dict:
    """
    End-to-end sanitization pipeline.

    Args:
        input_path: path to the input CSV file
        output_path: path to write the redacted CSV
        sample_rows: optionally restrict to first N rows
        use_ner: whether to run NER in addition to regex
        token: replacement string for redactions

    Returns:
        RedactionSummary dict
    """
    # 1) Load data
    df = read_csv(input_path, sample_rows)

    # 2) Regex detections
    regex_hits = detect_regex(df)

    # 3) Which columns are text?
    text_cols = get_text_columns(df)

    # 4) NER detections
    ner_hits = detect_ner(df, text_cols, model=load_ner()) if use_ner else []

    # 5) Combine + dedupe overlaps
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
    parser.add_argument("--no-ner", action="store_true", help="Disable NER")
    parser.add_argument("--token", default="[REDACTED]", help="Replacement token")
    args = parser.parse_args()

    summary = sanitize_file(
        input_path=args.input,
        output_path=args.output,
        sample_rows=args.sample,
        use_ner=not args.no_ner,
        token=args.token
    )

    print("Redaction summary:")
    print(summary)


if __name__ == "__main__":
    main()
