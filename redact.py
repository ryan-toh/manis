from __future__ import annotations

from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import pandas as pd

from common import Detection, RedactionSummary

def _length(d: Detection) -> int:
    return d.end - d.start

def _coalesce_spans(spans: List[Detection]) -> List[Detection]:

    if not spans:
        return []

    spans = sorted(spans, key=lambda d: (d.start, -_length(d)))

    merged: List[Detection] = []
    for d in spans:
        if not merged:
            merged.append(d)
            continue

        last = merged[-1]
        if d.start > last.end:
            merged.append(d)
            continue

        new_start = min(last.start, d.start)
        new_end = max(last.end, d.end)

        last_len = last.end - last.start
        d_len = d.end - d.start
        if d_len > last_len:
            chosen_label = d.label
            chosen_value = d.value
        else:
            chosen_label = last.label
            chosen_value = last.value

        merged[-1] = Detection(
            row=last.row,
            col=last.col,
            start=new_start,
            end=new_end,
            label=chosen_label,
            value=chosen_value,
        )

    return merged

def dedupe_overlaps(detections: List[Detection]) -> List[Detection]:
    by_cell: Dict[Tuple[int, str], List[Detection]] = defaultdict(list)
    for d in detections:
        by_cell[(d.row, d.col)].append(d)

    cleaned: List[Detection] = []
    for (row, col), spans in by_cell.items():
        # Ensure spans belong to the same cell
        spans = [s for s in spans if s.row == row and s.col == col]
        cleaned.extend(_coalesce_spans(spans))

    return cleaned

def _apply_cell(text: str, spans: List[Detection], token: str) -> Tuple[str, int]:
    if not spans or not text:
        return text, 0

    # Sort descending by start so we can slice safely
    spans_sorted = sorted(spans, key=lambda d: d.start, reverse=True)
    replaced = 0
    for d in spans_sorted:
        # Guard against pathological indices; upstream should prevent this,
        # but we keep it defensive in case of unexpected input.
        s, e = max(0, d.start), max(0, d.end)
        if s >= e or s >= len(text):
            continue
        e = min(e, len(text))
        text = text[:s] + token + text[e:]
        replaced += 1
    return text, replaced

def apply_redactions(
        df: pd.DataFrame,
        detections: List[Detection],
        token: str = "[REDACTED]",
) -> Tuple[pd.DataFrame, RedactionSummary]:

    out = df.copy()

    cell_map: Dict[Tuple[int, str], List[Detection]] = defaultdict(list)
    for d in detections:
        cell_map[(d.row, d.col)].append(d)

    label_counter = Counter()
    col_counter = Counter()
    total = 0

    for (row, col), spans in cell_map.items():
        spans = _coalesce_spans(spans)

        try:
            original = out.at[row, col]
        except Exception:
            continue

        text = "" if original is None else str(original)

        new_text, count = _apply_cell(text, spans, token)
        if count > 0:
            out.at[row, col] = new_text
            total += count
            col_counter[col] += count
            for d in spans:
                label_counter[d.label] += 1

    summary: RedactionSummary = {
        "total": {"count": int(total)},
        "by_label": {k: int(v) for k, v in label_counter.items()},
        "by_column": {k: int(v) for k, v in col_counter.items()},
    }

    return out, summary