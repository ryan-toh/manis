import pandas as pd
from typing import List, Optional

def read_csv(path: str, sample_rows: Optional[int] = None) -> pd.DataFrame:
    df = pd.read_csv(path, dtype = str)
    if sample_rows:
        df = df.head(sample_rows)
    return df

def get_text_columns(df: pd.DataFrame, min_text_ratio: float = 0.6) -> List[str]:
    text_cols = []
    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            continue
        str_count = series.apply(lambda x: isinstance(x, str)).sum()
        ratio = str_count / len(series)
        if ratio >= min_text_ratio:
            text_cols.append(col)
    return text_cols
