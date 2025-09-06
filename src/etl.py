from pathlib import Path
from datetime import datetime
import pandas as pd

def _kpi(df, score_col):
    s = df[score_col].dropna()
    total = len(s)
    green = (s >= 90).sum()
    amber = ((s >= 70) & (s < 90)).sum()
    red = (s < 70).sum()
    readiness = round(s.mean(), 1) if total else 0
    return dict(total=total, green=green, amber=amber, red=red, readiness=readiness)

def _append_history(out_dir, kpi27001, kpi27701):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    hist = out / "summary_history.csv"
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "27001_total": kpi27001["total"], "27001_readiness": kpi27001["readiness"],
        "27701_total": kpi27701["total"], "27701_readiness": kpi27701["readiness"]
    }
    df = pd.DataFrame([row])
    mode, header = ("a", False) if hist.exists() else ("w", True)
    try:
        df.to_csv(hist, mode=mode, header=header, index=False, encoding="utf-8")
    except PermissionError:
        # excel lock fallback
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(out / f"summary_history_{ts}.csv", index=False, encoding="utf-8")

def run_etl(cfg):
    xls = pd.ExcelFile(cfg["input_file"])
    df27001 = pd.read_excel(xls, cfg["sheets"]["iso27001"])
    df27701 = pd.read_excel(xls, cfg["sheets"]["iso27701"])
    k1 = _kpi(df27001, cfg["score_column"])
    k2 = _kpi(df27701, cfg["score_column"])
    _append_history(cfg["output_folder"], k1, k2)
    return k1, k2
