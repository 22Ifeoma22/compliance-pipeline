import os, yaml, pandas as pd
from .metrics import kpis
from .visuals import bar_distribution
from .utils import get_logger, timestamp

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def extract(cfg):
    xls = pd.ExcelFile(cfg["input_file"])
    df27001 = pd.read_excel(xls, cfg["sheets"]["iso27001"])
    df27701 = pd.read_excel(xls, cfg["sheets"]["iso27701"])
    return df27001, df27701

def transform(df, score_col):
    # Clean column names; ensure score numeric
    df = df.copy()
    df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
    return df

def load_outputs(cfg, kpi27001, kpi27701):
    outdir = cfg["output_folder"]
    os.makedirs(outdir, exist_ok=True)
    # Save a tiny CSV summary each run (append-friendly)
    summary_path = os.path.join(outdir, "summary_history.csv")
    row = {
        "timestamp": timestamp(),
        "27001_total": kpi27001["total"], "27001_readiness": kpi27001["readiness"],
        "27701_total": kpi27701["total"], "27701_readiness": kpi27701["readiness"]
    }
    (pd.DataFrame([row])
       .to_csv(summary_path, mode="a", index=False, header=not os.path.exists(summary_path)))

def generate_visuals(cfg, kpi27001, kpi27701):
    outdir = cfg["output_folder"]
    bar_distribution(kpi27001, "ISO 27001 – Distribution",
                     os.path.join(outdir, "iso27001_distribution.png"))
    bar_distribution(kpi27701, "ISO 27701 – Distribution",
                     os.path.join(outdir, "iso27701_distribution.png"))

def run():
    log = get_logger()
    cfg = load_config()
    log.info("Starting pipeline…")
    df27001, df27701 = extract(cfg)
    score_col = cfg["score_column"]

    df27001 = transform(df27001, score_col)
    df27701 = transform(df27701, score_col)

    kpi27001 = kpis(df27001, score_col)
    kpi27701 = kpis(df27701, score_col)
    log.info(f"KPI 27001: {kpi27001}")
    log.info(f"KPI 27701: {kpi27701}")

    load_outputs(cfg, kpi27001, kpi27701)
    generate_visuals(cfg, kpi27001, kpi27701)
    log.info("Pipeline complete.")
