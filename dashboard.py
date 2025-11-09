import streamlit as st
import pandas as pd
import glob
import os
from datetime import datetime

# -------------------------------
# Config
# -------------------------------
files = glob.glob("output/kospi_kosdaq_technical_*.csv")
if not files:
    st.error("No CSV files found in output/")
    st.stop()
DATA_FILE = max(files, key=os.path.getctime)
FETCH_TIME = "17:30 KST (after market close)"

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="Pearl Screener Dashboard", layout="wide")

# -------------------------------
# Headline section
# -------------------------------
st.markdown("# 📈 KOSPI–KOSDAQ Livermore Pearl Screener")
st.markdown("""
A technical analysis dashboard inspired by **Livermore trading principles** and tailored for the Korean markets.  
This screener highlights potential pearls by combining **VolumeSpike**, **TrendArrow**, and **PearlScore**.
""")

st.markdown(f"ℹ️ Data last fetched by GitHub Action at **{FETCH_TIME}**")

# -------------------------------
# Load and prepare data
# -------------------------------
df = pd.read_csv(DATA_FILE)

use_cols = [
    "StockCode", "StockName_KR", "ClosingPrice", "VolumeSpike", "TrendArrow",
    "PearlScore_Normalized", "PearlScore_Stars", "PearlScore_Status"
]
missing = [c for c in use_cols if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

df = df[use_cols].copy()

# -------------------------------
# Styling helpers
# -------------------------------
def color_trend(val):
    if val == "↑":
        return "color: red; font-weight: bold;"
    elif val == "↓":
        return "color: blue; font-weight: bold;"
    elif val == "→":
        return "color: black; font-weight: bold;"
    return ""

def color_stars(val):
    if isinstance(val, str) and "★" in val:
        return "color: goldenrod; font-weight: bold;"
    return ""

def highlight_missing(row):
    if row["PearlScore_Status"] == "Data Missing":
        return ["background-color: lightgray"] * len(row)
    return [""] * len(row)

# -------------------------------
# Summary panel: Top 10 / Bottom 10
# -------------------------------
if not df.empty:
    top10 = df.sort_values(by="PearlScore_Normalized", ascending=False).head(10)
    bottom10 = df.sort_values(by="PearlScore_Normalized", ascending=True).head(10)

    st.markdown("## 🌟 Top 10 Pearls")
    styled_top10 = (
        top10[["StockName_KR", "StockCode", "ClosingPrice", "VolumeSpike", "TrendArrow", "PearlScore_Stars", "PearlScore_Normalized"]]
        .style
        .applymap(color_trend, subset=["TrendArrow"])
        .applymap(color_stars, subset=["PearlScore_Stars"])
    )
    st.dataframe(styled_top10, use_container_width=True)

    st.markdown("## 🪙 Bottom 10 Pearls")
    styled_bottom10 = (
        bottom10[["StockName_KR", "StockCode", "ClosingPrice", "VolumeSpike", "TrendArrow", "PearlScore_Stars", "PearlScore_Normalized"]]
        .style
        .applymap(color_trend, subset=["TrendArrow"])
        .applymap(color_stars, subset=["PearlScore_Stars"])
    )
    st.dataframe(styled_bottom10, use_container_width=True)

# -------------------------------
# Filters
# -------------------------------
st.markdown("## 🔎 Filter Your Screener Results")

c1, c2, c3 = st.columns(3)
with c1:
    vol_spike_min = st.number_input("Min VolumeSpike", value=1.0, step=0.1)
with c2:
    pearl_score_min = st.number_input("Min PearlScore (Normalized)", value=50.0, step=1.0)
with c3:
    arrow_filter = st.selectbox("TrendArrow Filter", options=["All", "↑", "↓", "→"])

# -------------------------------
# Apply filters
# -------------------------------
filtered = df.copy()

# Arrow filter first (so ↑, ↓, → all show naturally)
if arrow_filter != "All":
    filtered = filtered[filtered["TrendArrow"] == arrow_filter]

# Then apply thresholds
filtered = filtered[
    (filtered["VolumeSpike"] >= vol_spike_min) &
    (filtered["PearlScore_Normalized"] >= pearl_score_min)
]

# -------------------------------
# Sort and prepare display
# -------------------------------
filtered = filtered.sort_values(by="PearlScore_Normalized", ascending=False).reset_index(drop=True)

# -------------------------------
# Conditional styling for main table
# -------------------------------
styled = (
    filtered.style
    .applymap(color_trend, subset=["TrendArrow"])
    .applymap(color_stars, subset=["PearlScore_Stars"])
    .apply(highlight_missing, axis=1)
)

# -------------------------------
# Show styled table
# -------------------------------
st.markdown("## 📊 Filtered Stocks")
st.dataframe(styled, use_container_width=True)

# -------------------------------
# Data export section (bottom)
# -------------------------------
st.markdown("## 💾 Save Your Results")
st.markdown("Download the currently filtered screener results as a CSV file for further analysis.")

csv = filtered.to_csv(index=False).encode("utf-8")

# meaningful filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"pearl_screener_filtered_{timestamp}.csv"

st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=csv,
    file_name=file_name,
    mime="text/csv",
)
