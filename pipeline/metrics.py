import pandas as pd

def kpis(df: pd.DataFrame, score_col: str):
    df = df.dropna(subset=[score_col]).copy()
    total = len(df)
    compliant = (df[score_col] >= 90).sum()
    partial   = ((df[score_col] >= 70) & (df[score_col] < 90)).sum()
    noncomp   = (df[score_col] < 70).sum()
    readiness = round(df[score_col].mean(), 1) if total else 0
    return {
        "total": total,
        "compliant": compliant,
        "partial": partial,
        "noncompliant": noncomp,
        "readiness": readiness
    }
