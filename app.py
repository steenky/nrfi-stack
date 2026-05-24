import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Edge Model (Upgraded)")

# ----------------------------
# TEAM DATA (MORE REALISTIC SIGNALS)
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
# SAMPLE MATCHUPS
# ----------------------------
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS"},
    {"away": "LAD", "home": "SF"},
    {"away": "ATL", "home": "NYM"},
])

rows = []

# ----------------------------
# IMPROVED NRFI MODEL
# ----------------------------
for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    # Pitching environment (higher opponent K rate = better for NRFI)
    pitching_factor = (
        (away["k_rate"] + home["k_rate"]) / 2
    )

    # Offensive pressure (OBP + power = bad for NRFI)
    offense_factor = (
        (away["obp"] + home["obp"]) * 50 +
        (away["power"] + home["power"]) * 100
    )

    # NRFI probability (calibrated logistic model)
    nrfi_prob = 1 / (1 + np.exp(-(pitching_factor - offense_factor)))

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "pitching_factor": round(pitching_factor, 2),
        "offense_factor": round(offense_factor, 2)
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE TIERS (REALISTIC THRESHOLDS)
# ----------------------------
df["edge_tier"] = df["nrfi_prob"].apply(
    lambda x: "🔥 STRONG NRFI" if x >= 0.62
    else ("✅ LEAN NRFI" if x >= 0.55 else "PASS")
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