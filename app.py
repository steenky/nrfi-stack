import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Edge Model (Betting Version)")

# ----------------------------
# TEAM DATA
# ----------------------------
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 23.5, "obp": 0.323, "power": 0.180},
    {"team": "BOS", "k_rate": 22.8, "obp": 0.318, "power": 0.175},
    {"team": "LAD", "k_rate": 20.9, "obp": 0.335, "power": 0.190},
    {"team": "SF",  "k_rate": 23.1, "obp": 0.310, "power": 0.165},
    {"team": "ATL", "k_rate": 21.0, "obp": 0.330, "power": 0.185},
    {"team": "NYM", "k_rate": 22.0, "obp": 0.315, "power": 0.172},
])

# ----------------------------
# MATCHUPS
# ----------------------------
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS"},
    {"away": "LAD", "home": "SF"},
    {"away": "ATL", "home": "NYM"},
])

rows = []

# ----------------------------
# MODEL
# ----------------------------
for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    pitching = (away["k_rate"] + home["k_rate"]) / 2 / 30
    offense = (away["obp"] + home["obp"]) / 2 + (away["power"] + home["power"]) / 4

    score = pitching - offense

    nrfi_prob = 1 / (1 + np.exp(-8 * score))

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE CALCULATION (REAL IMPROVEMENT)
# ----------------------------
league_avg = 0.52

df["edge"] = df["nrfi_prob"] - league_avg

df["edge_tier"] = df["edge"].apply(
    lambda x: "🔥 STRONG NRFI" if x >= 0.05
    else ("✅ LEAN NRFI" if x >= 0.02 else "PASS")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("All Games")
st.dataframe(df)

st.subheader("🔥 Best Plays (Positive Edge Only)")

best = df[df["edge"] >= 0.05]

if best.empty:
    best = df.sort_values("edge", ascending=False).head(2)

st.dataframe(best)

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")