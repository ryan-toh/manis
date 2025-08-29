# justin's work

import pandas as pd
from typing import List, Optional

def read_csv(path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Load a CSV. If sample_rows is given, return only the first N rows.
    Input:  path -> 'data/input.csv'
            sample_rows -> e.g. 5000 or None
    Output: pandas DataFrame (object dtypes for text columns)
    """
    df = pd.read_csv(path, dtype = str)
    if sample_rows:
        df = df.head(sample_rows)
    return df

def get_text_columns(df: pd.DataFrame, min_text_ratio: float = 0.6) -> List[str]:
    """
    Heuristic to pick columns that look like text (strings) vs numeric.
    Input:  df
            min_text_ratio -> fraction of non-null rows that must be strings
    Output: list of column names (e.g. ['notes', 'description'])
    """
    text_cols = []
    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            continue
        # Count fraction of entries that are non-numeric strings
        str_count = series.apply(lambda x: isinstance(x, str)).sum()
        ratio = str_count / len(series)
        if ratio >= min_text_ratio:
            text_cols.append(col)
    return text_cols