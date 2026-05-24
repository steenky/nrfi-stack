import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Pro Betting Model (Final Version)")

# ----------------------------
# TEAM BASE DATA (STABLE PROXIES)
# ----------------------------
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 23.5, "bb_rate": 7.8, "obp": 0.323, "power": 0.180, "bullpen": 0.72},
    {"team": "BOS", "k_rate": 22.8, "bb_rate": 8.9, "obp": 0.318, "power": 0.175, "bullpen": 0.65},
    {"team": "LAD", "k_rate": 20.9, "bb_rate": 6.5, "obp": 0.335, "power": 0.190, "bullpen": 0.78},
    {"team": "SF",  "k_rate": 23.1, "bb_rate": 7.5, "obp": 0.310, "power": 0.165, "bullpen": 0.70},
    {"team": "ATL", "k_rate": 21.0, "bb_rate": 7.0, "obp": 0.330, "power": 0.185, "bullpen": 0.74},
    {"team": "NYM", "k_rate": 22.0, "bb_rate": 8.2, "obp": 0.315, "power": 0.172, "bullpen": 0.66},
])

# ----------------------------
# MATCHUPS + ODDS
# ----------------------------
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS", "odds": -120},
    {"away": "LAD", "home": "SF", "odds": -110},
    {"away": "ATL", "home": "NYM", "odds": -115},
])

# ----------------------------
# ODDS CONVERSION
# ----------------------------
def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)

# ----------------------------
# MODEL CORE
# ----------------------------
rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    # ----------------------------
    # PITCHING STRENGTH (K-BB STYLE)
    # ----------------------------
    away_pitch = (away["k_rate"] - away["bb_rate"]) / 30
    home_pitch = (home["k_rate"] - home["bb_rate"]) / 30

    pitching_strength = (away_pitch + home_pitch) / 2

    # ----------------------------
    # OFFENSE PRESSURE
    # ----------------------------
    offense_pressure = (
        (away["obp"] + home["obp"]) / 2 * 0.6 +
        (away["power"] + home["power"]) / 4 * 0.4
    )

    # ----------------------------
    # PARK + BULLPEN FACTOR (SIMPLIFIED)
    # ----------------------------
    bullpen_factor = (away["bullpen"] + home["bullpen"]) / 2

    # higher bullpen = better NRFI support
    environment = bullpen_factor * 0.25

    # ----------------------------
    # FINAL MODEL SCORE
    # ----------------------------
    score = pitching_strength + environment - offense_pressure

    # CALIBRATED PROBABILITY
    nrfi_prob = 1 / (1 + np.exp(-6 * score))

    # ----------------------------
    # ODDS + EV
    # ----------------------------
    decimal_odds = odds_to_decimal(g["odds"])
    implied_prob = 1 / decimal_odds

    ev = (nrfi_prob * (decimal_odds - 1)) - (1 - nrfi_prob)

    # BET SIZING (KELLY FRACTION LIGHT)
    kelly = max((nrfi_prob * decimal_odds - 1) / (decimal_odds - 1), 0)

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied_prob, 3),
        "edge_ev": round(ev, 3),
        "kelly_pct": round(kelly * 100, 1),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE CLASSIFICATION
# ----------------------------
df["tier"] = df["edge_ev"].apply(
    lambda x: "🔥 STRONG BET" if x > 0.05
    else ("✅ LEAN" if x > 0 else "❌ NO BET")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("All NRFI Bets (Final Model)")
st.dataframe(df)

st.subheader("🔥 Recommended Bets (+EV Only)")

best = df[df["edge_ev"] > 0.05]

if best.empty:
    best = df.sort_values("edge_ev", ascending=False).head(2)

st.dataframe(best)

st.subheader("📊 Betting Notes")

st.write(
    "Kelly % suggests relative stake sizing. Keep bets small (0.5–2% bankroll max per play)."
)

st.caption(f"Last updated: {df['timestamp'].iloc[0]}")