from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import pandas as pd

@dataclass
class Detection:
    row: int            # DataFrame row index
    col: str            # column name
    start: int          # character start (inclusive) in the cell text
    end: int            # character end (exclusive)
    label: str          # e.g. 'EMAIL', 'PHONE', 'CREDIT_CARD', 'IP', 'PERSON', 'ORG', 'LOCATION'
    value: str          # the exact matched text

# Summary structure returned after redaction
RedactionSummary = Dict[str, Dict[str, int]]
# example:
# {
#   "total": {"count": 42},
#   "by_label": {"EMAIL": 10, "PHONE": 5, ...},
#   "by_column": {"notes": 20, "email": 10, ...}
# }


### ingest.py
# import pandas as pd
# from typing import List, Optional

# def read_csv(path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
#     """
#     Load a CSV. If sample_rows is given, return only the first N rows.
#     Input:  path -> 'data/input.csv'
#             sample_rows -> e.g. 5000 or None
#     Output: pandas DataFrame (object dtypes for text columns)
#     """

# def get_text_columns(df: pd.DataFrame, min_text_ratio: float = 0.6) -> List[str]:
#     """
#     Heuristic to pick columns that look like text (strings) vs numeric.
#     Input:  df
#             min_text_ratio -> fraction of non-null rows that must be strings
#     Output: list of column names (e.g. ['notes', 'description'])
#     """


### regex.py
# from typing import List, Optional
# import pandas as pd
# from .types import Detection  # or import Detection from a shared place

# def detect_regex(
#     df: pd.DataFrame,
#     columns: Optional[List[str]] = None
# ) -> List[Detection]:
#     """
#     Run built-in regexes for EMAIL, PHONE, CREDIT_CARD, IP on the chosen columns.
#     Input:  df
#             columns -> list of columns to scan; if None, scan all df columns that are strings
#     Output: list of Detection objects
#     """

# # (Optional helpers you might expose, but not required by the CLI)
# def find_emails(text: str) -> List[Tuple[int, int, str]]: ...
# def find_phones(text: str) -> List[Tuple[int, int, str]]: ...
# def find_credit_cards(text: str) -> List[Tuple[int, int, str]]: ...
# def find_ips(text: str) -> List[Tuple[int, int, str]]: ...
# # Each returns a list of (start, end, value) for a single string.


### ner.py
# from typing import Iterable, List, Optional
# import pandas as pd
# from .types import Detection

# def load_ner(model_name: str = "en_core_web_sm"):
#     """
#     Load and return the NER model (spaCy pipeline or similar).
#     Input:  model_name -> spaCy model name
#     Output: model object (opaque to callers)
#     """

# def detect_ner(
#     df: pd.DataFrame,
#     text_columns: List[str],
#     model=None,
#     labels: Iterable[str] = ("PERSON", "ORG", "GPE")
# ) -> List[Detection]:
#     """
#     Run NER over the given text columns and collect PERSON/ORG/LOCATION (GPE).
#     Input:  df
#             text_columns -> which columns to scan (strings)
#             model -> from load_ner(); if None, load inside
#             labels -> which entity labels to keep
#     Output: list of Detection objects
#     """

### redact.py
# from typing import List, Tuple
# import pandas as pd
# from .types import Detection, RedactionSummary
# from collections import Counter

# def apply_redactions(
#     df: pd.DataFrame,
#     detections: List[Detection],
#     token: str = "[REDACTED]"
# ) -> Tuple[pd.DataFrame, RedactionSummary]:
#     """
#     Replace the detected spans in string cells with token.
#     IMPORTANT: Sort and replace right-to-left within each cell to keep indices valid.
#     Input:  df
#             detections -> list from regex + ner
#             token -> replacement string
#     Output: (redacted_df, summary)
#             summary['total']['count'] = total replacements
#             summary['by_label'][label] = count per PII type
#             summary['by_column'][col] = count per column
#     """

# def dedupe_overlaps(detections: List[Detection]) -> List[Detection]:
#     """
#     (Optional) Merge or drop overlapping spans to avoid double replacement.
#     Input:  detections
#     Output: cleaned list of detections
#     """

### sanitize.py
# import argparse
# from typing import Optional
# import pandas as pd

# from pipeline.ingest import read_csv, get_text_columns
# from detect.regex import detect_regex
# from detect.ner import load_ner, detect_ner
# from transform.redact import apply_redactions, dedupe_overlaps

# def sanitize_file(
#     input_path: str,
#     output_path: str,
#     sample_rows: Optional[int] = None,
#     use_ner: bool = True,
#     token: str = "[REDACTED]"
# ) -> dict:
#     """
#     End-to-end sanitization.
#     Input:  input_path, output_path, sample_rows, use_ner, token
#     Output: summary dict (same as RedactionSummary plus maybe file info)
#     Steps:
#       1) df = read_csv(input_path, sample_rows)
#       2) regex_hits = detect_regex(df)
#       3) text_cols = get_text_columns(df)
#       4) ner_hits = detect_ner(df, text_cols, model=load_ner()) if use_ner else []
#       5) hits = dedupe_overlaps(regex_hits + ner_hits)
#       6) redacted_df, summary = apply_redactions(df, hits, token)
#       7) redacted_df.to_csv(output_path, index=False)
#       8) return summary
#     """

# def main():
#     parser = argparse.ArgumentParser(description="Redact PII from a CSV.")
#     parser.add_argument("input", help="Path to input CSV")
#     parser.add_argument("output", help="Path to write redacted CSV")
#     parser.add_argument("--sample", type=int, default=None, help="Limit to first N rows")
#     parser.add_argument("--no-ner", action="store_true", help="Disable NER")
#     parser.add_argument("--token", default="[REDACTED]", help="Replacement token")
#     args = parser.parse_args()

#     summary = sanitize_file(
#         input_path=args.input,
#         output_path=args.output,
#         sample_rows=args.sample,
#         use_ner=not args.no_ner,
#         token=args.token
#     )
#     # Print a tiny human summary
#     print("Redaction summary:", summary)

# if __name__ == "__main__":
#     main()


### Minimal success criteria (what to test once)

# Put a tiny CSV with fake data:
"""
name,email,notes
Alice,alice@example.com,"Call me at 555-123-4567"
"""

# Run
"""
python -m src.cli.sanitize data/input.csv out/redacted.csv --sample 1000
"""