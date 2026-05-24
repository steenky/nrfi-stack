import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Predictor (Stable Version)")

# ----------------------------
# STATIC MLB SLATE
# ----------------------------
df = pd.DataFrame([
    {"away_team": "Yankees", "home_team": "Red Sox", "away_pitcher": "Cole", "home_pitcher": "Bello"},
    {"away_team": "Dodgers", "home_team": "Giants", "away_pitcher": "Yamamoto", "home_pitcher": "Webb"},
    {"away_team": "Braves", "home_team": "Mets", "away_pitcher": "Strider", "home_pitcher": "Senga"},
    {"away_team": "Astros", "home_team": "Rangers", "away_pitcher": "Valdez", "home_pitcher": "Eovaldi"},
    {"away_team": "Cubs", "home_team": "Cardinals", "away_pitcher": "Steele", "home_pitcher": "Gray"},
    {"away_team": "Mariners", "home_team": "Angels", "away_pitcher": "Kirby", "home_pitcher": "Sandoval"},
    {"away_team": "Phillies", "home_team": "Nationals", "away_pitcher": "Wheeler", "home_pitcher": "Gore"},
])

# ----------------------------
# SIMULATED MODEL (STABLE)
# ----------------------------
np.random.seed(42)

df["pitcher_score"] = np.random.uniform(0.45, 0.80, len(df))
df["offense_score"] = np.random.uniform(0.45, 0.80, len(df))
df["park_score"] = np.random.uniform(0.45, 0.80, len(df))

df["avg_nrfi"] = (
    df["pitcher_score"] * 0.50
    - df["offense_score"] * 0.30
    - (1 - df["park_score"]) * 0.20
)

# ----------------------------
# EDGE LOGIC (ALWAYS RETURNS RESULTS)
# ----------------------------
q70 = df["avg_nrfi"].quantile(0.70)
q40 = df["avg_nrfi"].quantile(0.40)

df["edge_tier"] = df["avg_nrfi"].apply(
    lambda x: "🔥 STRONG NRFI" if x >= q70
    else ("✅ LEAN NRFI" if x >= q40 else "PASS")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("All Games")
st.dataframe(df)

st.subheader("🔥 Best Plays")

best = df[df["edge_tier"] == "🔥 STRONG NRFI"]

# fallback so it NEVER goes empty
if best.empty:
    best = df.sort_values("avg_nrfi", ascending=False).head(2)

st.dataframe(best)

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")