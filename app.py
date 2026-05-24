import streamlit as st
import pandas as pd
from datetime import datetime
from pybaseball import pitching_stats

st.title("⚾ NRFI Predictor (Live MLB Data)")

# -----------------------------
# LOAD REAL PITCHER DATA
# -----------------------------
@st.cache_data(ttl=86400)
def get_pitchers():
    df = pitching_stats(2025)
    return df

df = get_pitchers()

# -----------------------------
# CLEAN + STANDARDIZE
# -----------------------------
df = df[[
    "Name",
    "Team",
    "K/9",
    "BB/9",
    "HR/9",
    "WHIP"
]].dropna()

df.columns = ["pitcher", "team", "k9", "bb9", "hr9", "whip"]

# -----------------------------
# SIMPLE NRFI SCORE MODEL
# -----------------------------
df["nrfi_score"] = (
    (df["k9"] * 0.35) -
    (df["bb9"] * 0.25) -
    (df["hr9"] * 0.35) -
    (df["whip"] * 0.10)
)

df["edge_tier"] = df["nrfi_score"].apply(
    lambda x: "🔥 STRONG NRFI" if x > 3.0
    else ("✅ LEAN NRFI" if x > 2.0 else "PASS")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# -----------------------------
# DISPLAY
# -----------------------------
st.subheader("All Pitchers")
st.dataframe(df.sort_values("nrfi_score", ascending=False))

st.subheader("🔥 Best NRFI Targets")
st.dataframe(df[df["edge_tier"] == "🔥 STRONG NRFI"])

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")