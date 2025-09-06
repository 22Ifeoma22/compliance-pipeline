# streamlit_app.py
from __future__ import annotations

import os, sys, io, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import yaml

# --- Make sure we can import from src/ ---
ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Your local modules
from etl import run as etl_run          # src/etl.py must expose run(cfg)
from visuals import plot_iso_bars       # src/visuals.py should expose plotting helpers

# --- Config & paths ---
CFG_FILE = ROOT / "config.yaml"

# Use a writable folder on Streamlit Cloud (and locally this still works)
TMP_DIR = Path(tempfile.gettempdir()) / "compliance_pipeline"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Helper: load config
def load_cfg():
    with open(CFG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

st.set_page_config(page_title="Compliance Metrics & Dashboard", layout="wide")

st.title("Compliance Metrics & Dashboard")
st.caption("ISO 27001 & 27701 KPIs • RAG status • trend history")

cfg = load_cfg()

# --- Input file: allow upload, else use repo sample if present, else generate demo ---
default_input = ROOT / cfg["input_file"]  # e.g. data/inputs/Tech_Compliance_DayToDay_Pack.xlsx

uploaded = st.file_uploader("Upload your Excel workbook (optional)", type=["xlsx"])
if uploaded:
    input_bytes = uploaded.read()
    input_path = TMP_DIR / "uploaded_input.xlsx"
    input_path.write_bytes(input_bytes)
elif default_input.exists():
    input_path = default_input
else:
    # Create a tiny demo Excel so the app always runs
    st.info("No input file found. Generating a small demo workbook.")
    demo = {
        "ISO27001 Annex A": pd.DataFrame({
            "Control": ["A.5", "A.6", "A.7", "A.8", "A.9"],
            "Compliance Score (%)": [92, 86, 74, 55, 98],
        }),
        "ISO27701 Annex A&B": pd.DataFrame({
            "Control": ["P.1", "P.2", "P.3", "P.4"],
            "Compliance Score (%)": [88, 60, 72, 95],
        }),
        "Metrics & Dashboard": pd.DataFrame({
            "timestamp": [pd.Timestamp.utcnow().floor("min")],
            "27001_total": [5], "27001_readiness": [3],
            "27701_total": [4], "27701_readiness": [2],
        }),
    }
    input_path = TMP_DIR / "demo.xlsx"
    with pd.ExcelWriter(input_path, engine="openpyxl") as xw:
        for sheet, df in demo.items():
            df.to_excel(xw, sheet_name=sheet, index=False)

# --- Run ETL into the temp output folder ---
# Force outputs to TMP_DIR regardless of config (Cloud needs writable fs)
cfg_effective = dict(cfg)
cfg_effective["output_folder"] = str(TMP_DIR)

with st.spinner("Running ETL…"):
    kpis, df27001, df27701, history_path = etl_run(input_path, cfg_effective)

st.success("ETL finished")

# --- KPI cards ---
kpi_cols = st.columns(4)
kpi_cols[0].metric("ISO 27001 controls", int(kpis["27001_total"]))
kpi_cols[1].metric("ISO 27001 ready", int(kpis["27001_readiness"]))
kpi_cols[2].metric("ISO 27701 controls", int(kpis["27701_total"]))
kpi_cols[3].metric("ISO 27701 ready", int(kpis["27701_readiness"]))

st.divider()

# --- Distribution charts ---
left, right = st.columns(2)

with left:
    st.subheader("ISO 27001 distribution")
    fig1 = plot_iso_bars(df27001, title="ISO 27001 Compliance (%)")
    st.plotly_chart(fig1, use_container_width=True)

with right:
    st.subheader("ISO 27701 distribution")
    fig2 = plot_iso_bars(df27701, title="ISO 27701 Compliance (%)")
    st.plotly_chart(fig2, use_container_width=True)

# --- Trend (history) ---
st.subheader("Compliance trend (auto-appended after each run)")
try:
    hist = pd.read_csv(history_path, parse_dates=["timestamp"])
    hist = hist.sort_values("timestamp")
    long = hist.melt("timestamp", var_name="metric", value_name="value")
    figt = px.line(long, x="timestamp", y="value", color="metric",
                   title="Summary history (from temp outputs)")
    st.plotly_chart(figt, use_container_width=True)
except Exception as e:
    st.warning(f"Could not read trend history yet: {e}")

# --- Download outputs (from temp) ---
st.download_button("Download summary_history.csv",
                   data=open(history_path, "rb").read(),
                   file_name="summary_history.csv",
                   mime="text/csv")
st.caption(f"Outputs are in: {TMP_DIR}")
