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

RedactionSummary = Dict[str, Dict[str, int]]
