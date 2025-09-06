# dashboard.py — Compliance Automation Dashboard (ISO 27001 & 27701)
# Run:  streamlit run dashboard.py
# --- Demo-data fallback so app works anywhere ---
from pathlib import Path
import pandas as pd
import numpy as np
import datetime as dt

DATA_DIR = Path("data")
INPUTS = DATA_DIR / "inputs"
OUTPUTS = DATA_DIR / "outputs"
INPUTS.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

summary_csv = OUTPUTS / "summary_history.csv"

def _make_demo_history(n=6):
    now = pd.Timestamp.now().floor("min")
    ts = pd.date_range(end=now, periods=n, freq="H")
    df = pd.DataFrame({
        "timestamp": ts,
        "27001_total": np.random.randint(5, 10, size=n),
        "27001_readiness": np.random.uniform(70, 95, size=n).round(1),
        "27701_total": np.random.randint(5, 10, size=n),
        "27701_readiness": np.random.uniform(65, 92, size=n).round(1),
    })
    return df

if not summary_csv.exists():
    demo = _make_demo_history()
    demo.to_csv(summary_csv, index=False)

# small helper to load history everywhere
def load_history():
    try:
        return pd.read_csv(summary_csv, parse_dates=["timestamp"])
    except Exception:
        return _make_demo_history()
# --- end demo fallback ---

import io
import json
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
CFG_PATH = ROOT / "config.yaml"
OUT_DIR = ROOT / "data" / "outputs"
HIST_CSV = OUT_DIR / "summary_history.csv"
XLSX = ROOT / "data" / "inputs" / "Tech_Compliance_DayToDay_Pack.xlsx"

st.set_page_config(page_title="Compliance Automation Dashboard", layout="wide", page_icon="📊")
st.title("📊 Compliance Automation Dashboard")
st.caption("ISO 27001 & 27701 • Data Protection • Risk & Trends")

# ---------- helpers ----------
def safe_read_history(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["timestamp","27001_total","27001_readiness","27701_total","27701_readiness"])
    df = pd.read_csv(path)
    # ensure sorted by time
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    return df

def safe_read_controls(xlsx_path: Path):
    if not xlsx_path.exists():
        return None, None
    try:
        xls = pd.ExcelFile(xlsx_path)
        df27001 = pd.read_excel(xls, "ISO27001 Annex A")
        df27701 = pd.read_excel(xls, "ISO27701 Annex A&B")
        return df27001, df27701
    except Exception:
        return None, None

def kpis_from_df(df: pd.DataFrame, score_col="Compliance Score (%)"):
    if df is None or df.empty or score_col not in df.columns:
        return dict(total=0, green=0, amber=0, red=0, readiness=0.0)
    s = pd.to_numeric(df[score_col], errors="coerce").dropna()
    total = len(s)
    green = int((s >= 90).sum())
    amber = int(((s >= 70) & (s < 90)).sum())
    red   = int((s < 70).sum())
    readiness = float(round(s.mean(), 1)) if total else 0.0
    return dict(total=total, green=green, amber=amber, red=red, readiness=readiness)

def to_download_bytes(df: pd.DataFrame, filename="data.csv"):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

# ---------- load data ----------
hist = safe_read_history(HIST_CSV)
df27001, df27701 = safe_read_controls(XLSX)

score_col = "Compliance Score (%)"
kpi1 = kpis_from_df(df27001, score_col)
kpi2 = kpis_from_df(df27701, score_col)

# ---------- sidebar filters ----------
st.sidebar.header("Filters")
framework = st.sidebar.selectbox("Framework", ["Overview","ISO 27001","ISO 27701"])
min_score = st.sidebar.slider("Min score filter", 0, 100, 0, step=5)
search = st.sidebar.text_input("Search Control ID / Objective")
st.sidebar.divider()
st.sidebar.write("Files")
st.sidebar.write(f"History CSV: `{HIST_CSV}`")
st.sidebar.write(f"Workbook: `{XLSX}`")

# ---------- KPI header ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("ISO 27001 Readiness", f"{kpi1['readiness']}%", delta=None)
col2.metric("ISO 27701 Readiness", f"{kpi2['readiness']}%", delta=None)

def latest_delta(series):
    if len(series) >= 2:
        return round(series.iloc[-1] - series.iloc[-2], 1)
    return 0.0

d27001 = latest_delta(hist["27001_readiness"]) if "27001_readiness" in hist else 0.0
d27701 = latest_delta(hist["27701_readiness"]) if "27701_readiness" in hist else 0.0
col3.metric("Δ 27001 vs last run", f"{d27001:+.1f}%")
col4.metric("Δ 27701 vs last run", f"{d27701:+.1f}%")

# ---------- trends ----------
st.subheader("📈 Readiness Trends")
if not hist.empty:
    tfig = px.line(
        hist,
        x="timestamp",
        y=[c for c in ["27001_readiness","27701_readiness"] if c in hist.columns],
        markers=True,
        labels={"value":"Readiness %","variable":"Standard","timestamp":"Run"},
        title="Readiness Over Time"
    )
    st.plotly_chart(tfig, use_container_width=True)
else:
    st.info("No history yet. Run your ETL to create `summary_history.csv`.")

# ---------- distributions + pies ----------
def draw_dist_and_pie(df, title):
    if df is None or df.empty or score_col not in df.columns:
        st.warning(f"{title}: No data.")
        return
    df["_score"] = pd.to_numeric(df[score_col], errors="coerce")
    filt = df["_score"] >= min_score
    if search:
        filt &= df.apply(lambda r: search.lower() in (str(r.get("Control ID",""))+str(r.get("Control Objective",""))).lower(), axis=1)
    sdf = df[filt].copy()

    # Distribution
    bins=[0,70,90,100]
    labels=["<70 (Red)","70–89 (Amber)","≥90 (Green)"]
    sdf["Bucket"] = pd.cut(sdf["_score"], bins=bins, labels=labels, include_lowest=True, right=False)
    bar = sdf["Bucket"].value_counts().reindex(labels, fill_value=0)
    bfig = px.bar(bar, x=bar.index, y=bar.values, text=bar.values, title=f"{title} — Score Distribution")
    bfig.update_traces(textposition="outside")
    st.plotly_chart(bfig, use_container_width=True)

    # Pie
    pie = px.pie(names=bar.index, values=bar.values, title=f"{title} — RAG Breakdown", hole=0.4)
    st.plotly_chart(pie, use_container_width=True)

    # Table preview + download
    with st.expander(f"View {title} controls"):
        view_cols = [c for c in ["Control ID","Control Objective","Implementation","Audit Evidence","Required Action","Gap Assessment","Progress Status",score_col] if c in sdf.columns]
        st.dataframe(sdf[view_cols], use_container_width=True)
        st.download_button(
            "Download filtered controls (CSV)",
            data=to_download_bytes(sdf[view_cols]),
            file_name=f"{title.replace(' ','_').lower()}_filtered.csv",
            mime="text/csv"
        )

# ---------- radar maturity (derived) ----------
def maturity_radar(df):
    # derive simple maturity by averaging bucketed scores per theme
    # themes inferred by keywords (quick but effective for demo)
    themes = {
        "Governance": ["policy","policies","management","roles"],
        "Risk": ["risk","threat","vulnerability"],
        "Controls": ["access","crypto","backup","monitor"],
        "Awareness": ["training","awareness"],
        "Monitoring": ["audit","logging","review","test"],
    }
    vals = []
    if df is None or df.empty or score_col not in df.columns:
        return None, None
    text = (df["Control Objective"].astype(str) if "Control Objective" in df.columns else pd.Series([""]*len(df)))
    score = pd.to_numeric(df[score_col], errors="coerce").fillna(0)
    for k, keys in themes.items():
        mask = text.str.lower().apply(lambda t: any(kw in t for kw in keys))
        vals.append(score[mask].mean() if mask.any() else 0)
    cats = list(themes.keys())
    return cats, [round(v if not np.isnan(v) else 0, 1) for v in vals]

st.subheader("🕸️ Maturity Radar")
left_r, right_r = st.columns(2)
with left_r:
    c1, v1 = maturity_radar(df27001)
    if c1:
        r1 = go.Figure()
        r1.add_trace(go.Scatterpolar(r=v1, theta=c1, fill='toself', name="ISO 27001"))
        r1.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])))
        r1.update_layout(title="ISO 27001 Maturity (inferred)")
        st.plotly_chart(r1, use_container_width=True)
    else:
        st.info("No ISO 27001 data for radar.")
with right_r:
    c2, v2 = maturity_radar(df27701)
    if c2:
        r2 = go.Figure()
        r2.add_trace(go.Scatterpolar(r=v2, theta=c2, fill='toself', name="ISO 27701"))
        r2.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])))
        r2.update_layout(title="ISO 27701 Maturity (inferred)")
        st.plotly_chart(r2, use_container_width=True)
    else:
        st.info("No ISO 27701 data for radar.")

# ---------- framework sections ----------
st.subheader("📚 Framework Views")
if framework in ["Overview","ISO 27001"]:
    draw_dist_and_pie(df27001, "ISO 27001")
if framework in ["Overview","ISO 27701"]:
    draw_dist_and_pie(df27701, "ISO 27701")

# ---------- risk heatmap (toy, if you have risk sheet later, wire here) ----------
st.subheader("🔥 Risk Heatmap (demo)")
risk_grid = pd.DataFrame(
    [(i,j,i*j) for i in range(1,6) for j in range(1,6)],
    columns=["Likelihood","Impact","Score"]
)
hfig = px.density_heatmap(risk_grid, x="Likelihood", y="Impact", z="Score",
                          color_continuous_scale="RdYlGn_r", title="Risk Matrix")
st.plotly_chart(hfig, use_container_width=True)

# ---------- downloads ----------
st.divider()
colx, coly = st.columns(2)
with colx:
    if not hist.empty:
        st.download_button("⬇️ Download history CSV", data=to_download_bytes(hist), file_name="summary_history.csv", mime="text/csv")
with coly:
    bundle = {
        "kpi_iso27001": kpi1, "kpi_iso27701": kpi2,
        "rows_27001": int(kpi1["total"]), "rows_27701": int(kpi2["total"])
    }
    st.download_button("⬇️ Download KPI JSON", data=json.dumps(bundle, indent=2), file_name="kpi_summary.json", mime="application/json")

st.success("✅ Live dashboard ready. Use the sidebar filters, export data, and demo the visuals in your interview.")
