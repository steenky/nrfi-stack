
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="NRFI Model Dashboard", layout="wide")

st.title("🔥 MLB NRFI Model Dashboard")

st.write("Daily No Run First Inning (NRFI) projections")

# -----------------------------
# Load data safely
# -----------------------------
file_path = "data/predictions.csv"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    st.warning("No predictions found yet. Run your model pipeline first.")
    
    # fallback sample data so app still works
    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "model1": 0.62,
            "model2": 0.70,
            "model3": 0.74,
        }
    ])

# -----------------------------
# Feature engineering in app
# -----------------------------
if "avg_nrfi" not in df.columns:
    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

# -----------------------------
# Sort by best NRFI plays
# -----------------------------
df = df.sort_values("avg_nrfi", ascending=False)

# -----------------------------
# Main table
# -----------------------------
st.subheader("📊 All Games (Ranked by NRFI Probability)")

st.dataframe(
    df[[
        "away_team",
        "home_team",
        "model1",
        "model2",
        "model3",
        "avg_nrfi"
    ]]
)

# -----------------------------
# Best plays filter
# -----------------------------
st.subheader("🔥 Best NRFI Picks")

best = df[df["avg_nrfi"] >= 0.65]

if len(best) > 0:
    st.dataframe(best)
else:
    st.write("No strong NRFI plays today based on current model thresholds.")

# -----------------------------
# Simple insights
# -----------------------------
st.subheader("📈 Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Games Analyzed", len(df))
col2.metric("Best NRFI Probability", round(df["avg_nrfi"].max(), 3))
col3.metric("Average NRFI", round(df["avg_nrfi"].mean(), 3))
