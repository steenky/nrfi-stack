import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI EV Betting Model")

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
    {"away": "NYY", "home": "BOS", "odds": -120},
    {"away": "LAD", "home": "SF", "odds": -110},
    {"away": "ATL", "home": "NYM", "odds": -115},
])

rows = []

# ----------------------------
# CONVERT ODDS → DECIMAL
# ----------------------------
def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    else:
        return 1 + (odds / 100)

# ----------------------------
# MODEL
# ----------------------------
for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    # Pitching strength
    pitching = (away["k_rate"] + home["k_rate"]) / 2 / 30

    # Offensive pressure
    offense = (away["obp"] + home["obp"]) / 2 + (away["power"] + home["power"]) / 4

    # NRFI probability
    score = pitching - offense
    nrfi_prob = 1 / (1 + np.exp(-8 * score))

    # ----------------------------
    # ODDS + EV CALCULATION
    # ----------------------------
    decimal_odds = odds_to_decimal(g["odds"])
    implied_prob = 1 / decimal_odds

    ev = (nrfi_prob * (decimal_odds - 1)) - (1 - nrfi_prob)

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied_prob, 3),
        "ev": round(ev, 3),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE CLASSIFICATION
# ----------------------------
df["edge_tier"] = df["ev"].apply(
    lambda x: "🔥 +EV PLAY" if x > 0.05
    else ("⚠️ SMALL EDGE" if x > 0 else "❌ NO BET")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("All Games (EV Model)")
st.dataframe(df)

st.subheader("🔥 Best +EV Plays")

best = df[df["ev"] > 0.05]

if best.empty:
    best = df.sort_values("ev", ascending=False).head(2)

st.dataframe(best)

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")