import pandas as pd
import plotly.express as px
import streamlit as st
st.caption("Tip: Use the filters in the sidebar to drill into owners, status and score.")

# -----------------------------
# Load Data (cached)
# -----------------------------
@st.cache_data(ttl=3600)
def load_kpis(path: str):
    return pd.read_csv(path)

df = load_kpis("data/sample_kpis.csv")

# -----------------------------
# Dashboard Title
# -----------------------------
st.set_page_config(page_title="Compliance & Risk Dashboard", layout="wide")
st.title("📊 Compliance & Risk Dashboard")
st.write("This dashboard shows key compliance KPIs, risk heatmaps, and AI audit alignment.")

# -----------------------------
# KPI Cards
# -----------------------------
status_counts = df["Status"].value_counts().to_dict()
col1, col2, col3, col4 = st.columns(4)
col1.metric("✔️ Completed", status_counts.get("Complete", 0))
col2.metric("⏳ In Progress", status_counts.get("In Progress", 0))
col3.metric("❌ Delayed", status_counts.get("Delayed", 0))
col4.metric("📝 Not Started", status_counts.get("Not Started", 0))

# -----------------------------
# Breach Callout
# -----------------------------
if (df["Score"] < 70).any():
    st.error("⚠️ At least one KPI is below target. See the ‘Delayed’ or ‘Not Started’ group.")
else:
    st.success("✅ All KPIs meet current thresholds.")

# -----------------------------
# Risk Heatmap
# -----------------------------
st.subheader("Risk Heatmap (Owner × Score)")
fig = px.bar(df, x="Owner", y="Score", color="Status", barmode="group")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Donut Chart
# -----------------------------
st.subheader("Controls Coverage")
coverage = df["Status"].value_counts().reset_index()
coverage.columns = ["Status", "Count"]
fig2 = px.pie(coverage, values="Count", names="Status", hole=0.55)
fig2.update_layout(showlegend=True, height=300, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig2, use_container_width=True)
from pathlib import Path

hist_path = Path("data/outputs/summary_history.csv")
if hist_path.exists():
    st.subheader("Readiness Trend (from history)")
    hist = pd.read_csv(hist_path, parse_dates=["timestamp"])
    # If your columns are named differently, adjust here:
    # columns: timestamp,27001_total,27001_readiness,27701_total,27701_readiness
    line = pd.melt(
        hist,
        id_vars="timestamp",
        value_vars=[c for c in hist.columns if c != "timestamp"],
        var_name="Metric",
        value_name="Value",
    )
    fig_trend = px.line(line, x="timestamp", y="Value", color="Metric")
    fig_trend.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("ℹ️ No trend file found at `data/outputs/summary_history.csv`. Add one to show readiness over time.")

# -----------------------------
# Data Table + Export
# -----------------------------
st.subheader("Detailed Table")
st.dataframe(df)

st.download_button(
    "⬇️ Download filtered table (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="compliance_filtered.csv",
    mime="text/csv",
)

st.subheader("Detailed Table")
st.dataframe(df_filtered, use_container_width=True)

st.download_button(
    "⬇️ Download filtered table (CSV)",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="compliance_filtered.csv",
    mime="text/csv",
)
