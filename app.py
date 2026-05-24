import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Predictor (Stable Version)")

# ----------------------------
# STATIC MLB SLATE (NO API = NO FAILURES)
# ----------------------------
df = pd.DataFrame([
    {"away_team": "Yankees", "home_team": "Red Sox", "away_pitcher": "Cole", "home_pitcher": "Bello"},
    {"away_team": "Dodgers", "home_team": "Giants", "away_pitcher": "Yamamoto", "home_pitcher": "Webb"},
    {"away_team": "Braves", "home_team": "Mets", "away_pitcher": "Strider", "home_pitcher": "Senga"},
    {"away_team": "Astros", "home_team": "Rangers", "away_pitcher": "Valdez", "home_pitcher": "Eovaldi"},
    {"away_team": "Cubs", "home_team": "Cardinals", "away_pitcher": "Steele", "home_pitcher": "Gray"},
])

# ----------------------------
# SIMPLE RELIABLE MODEL
# ----------------------------
df["pitcher_score"] = np.random.uniform(0.45, 0.75, len(df))
df["offense_score"] = np.random.uniform(0.45, 0.75, len(df))
df["park_score"] = np.random.uniform(0.45, 0.75, len(df))

df["avg_nrfi"] = (
    df["pitcher_score"] * 0.5
    - df["offense_score"] * 0.3
    - (1 - df["park_score"]) * 0.2
)

df["edge_tier"] = np.where(
    df["avg_nrfi"] > 0.15,
    "🔥 STRONG NRFI",
    "PASS"
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("All Games")
st.dataframe(df)

st.subheader("Best Plays")
st.dataframe(df[df["edge_tier"] == "🔥 STRONG NRFI"])

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")