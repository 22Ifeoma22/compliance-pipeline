import streamlit as st
import pandas as pd
import plotly.express as px

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Compliance Dashboard",
    page_icon="✅",
    layout="wide"
)

# ---- HEADER ----
st.title("📊 Compliance & Risk Dashboard")
st.markdown("This dashboard shows key compliance KPIs, risk heatmaps, and AI audit alignment.")

# ---- LOAD DATA (fallback to sample data if missing) ----
try:
    df = pd.read_csv("data/sample_kpis.csv")
except Exception:
    df = pd.DataFrame({
        "Owner": ["Risk", "Compliance", "Legal", "IT"],
        "Status": ["Complete", "In Progress", "Delayed", "Not Started"],
        "Score": [95, 70, 55, 30]
    })

# ---- KPI CARDS ----
col1, col2, col3 = st.columns(3)
col1.metric("✔️ Completed", df[df["Status"] == "Complete"].shape[0])
col2.metric("⏳ In Progress", df[df["Status"] == "In Progress"].shape[0])
col3.metric("❌ Delayed", df[df["Status"] == "Delayed"].shape[0])

# ---- RISK HEATMAP ----
st.subheader("Risk Heatmap (Owner × Score)")
fig = px.bar(df, x="Owner", y="Score", color="Status", barmode="group")
st.plotly_chart(fig, use_container_width=True)

# ---- EXPORT OPTION ----
st.download_button(
    label="⬇️ Export KPI Data (CSV)",
    data=df.to_csv(index=False),
    file_name="compliance_kpis.csv",
    mime="text/csv",
)
import pandas as pd
import os

DATA_PATH = "data/sample_kpis.csv"

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        st.warning("No data file found, loading empty dataframe.")
        return pd.DataFrame()

df = load_data()
