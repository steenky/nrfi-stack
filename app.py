import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Predictor (Stable Betting Model)")

# ----------------------------
# STATIC RELIABLE MLB DATA (NO SCRAPING)
# ----------------------------
pitchers = pd.DataFrame([
    {"team": "NYY", "k_rate": 26.5, "bb_rate": 7.8, "hr9": 0.9},
    {"team": "BOS", "k_rate": 23.1, "bb_rate": 8.9, "hr9": 1.2},
    {"team": "LAD", "k_rate": 27.2, "bb_rate": 6.5, "hr9": 0.8},
    {"team": "SF",  "k_rate": 24.0, "bb_rate": 7.5, "hr9": 1.0},
    {"team": "ATL", "k_rate": 25.8, "bb_rate": 7.0, "hr9": 0.95},
    {"team": "NYM", "k_rate": 25.0, "bb_rate": 8.2, "hr9": 1.1},
])

batting = pd.DataFrame([
    {"team": "NYY", "k_rate": 22.5, "obp": 0.323},
    {"team": "BOS", "k_rate": 21.8, "obp": 0.318},
    {"team": "LAD", "k_rate": 20.9, "obp": 0.335},
    {"team": "SF",  "k_rate": 23.1, "obp": 0.310},
    {"team": "ATL", "k_rate": 21.0, "obp": 0.330},
    {"team": "NYM", "k_rate": 22.0, "obp": 0.315},
])

# ----------------------------
# SAMPLE GAMES
# ----------------------------
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS"},
    {"away": "LAD", "home": "SF"},
    {"away": "ATL", "home": "NYM"},
])

rows = []

# ----------------------------
# NRFI MODEL (STABLE MATH ONLY)
# ----------------------------
for _, g in games.iterrows():

    away_p = pitchers[pitchers["team"] == g["away"]].iloc[0]
    home_p = pitchers[pitchers["team"] == g["home"]].iloc[0]

    away_o = batting[batting["team"] == g["away"]].iloc[0]
    home_o = batting[batting["team"] == g["home"]].iloc[0]

    pitcher_score = (
        (away_p["k_rate"] + home_p["k_rate"]) * 0.4
        - (away_p["bb_rate"] + home_p["bb_rate"]) * 0.3
        - (away_p["hr9"] + home_p["hr9"]) * 10
    )

    offense_risk = (
        away_o["obp"] * 100 + away_o["k_rate"] * 0.2 +
        home_o["obp"] * 100 + home_o["k_rate"] * 0.2
    )

    nrfi_prob = 1 / (1 + np.exp(-(pitcher_score - offense_risk / 2)))

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "pitcher_score": round(pitcher_score, 2),
        "offense_risk": round(offense_risk, 2)
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE LOGIC
# ----------------------------
q70 = df["nrfi_prob"].quantile(0.70)
q40 = df["nrfi_prob"].quantile(0.40)

df["edge_tier"] = df["nrfi_prob"].apply(
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

if best.empty:
    best = df.sort_values("nrfi_prob", ascending=False).head(2)

st.dataframe(best)

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")