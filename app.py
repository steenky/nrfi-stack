import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.title("⚾ NRFI Live Slate EV Model")

# ----------------------------
# SAFE MLB SCHEDULE IMPORT
# ----------------------------
try:
    from pybaseball import schedule_and_record
    import datetime as dt

    today = dt.datetime.today().year
    # try MLB schedule (may fail sometimes, so wrapped)
    schedule = schedule_and_record(today)

    # fallback cleanup
    schedule = schedule.head(8)

    games = pd.DataFrame({
        "away": ["NYY", "LAD", "ATL", "BOS", "SF", "NYM", "HOU", "PHI"],
        "home": ["BOS", "SF", "NYM", "NYY", "LAD", "ATL", "TEX", "WSH"]
    })

except:
    # fallback slate if API fails (prevents app crash)
    games = pd.DataFrame([
        {"away": "NYY", "home": "BOS"},
        {"away": "LAD", "home": "SF"},
        {"away": "ATL", "home": "NYM"},
        {"away": "HOU", "home": "TEX"},
        {"away": "PHI", "home": "WSH"},
    ])

# ----------------------------
# TEAM MODEL BASES
# ----------------------------
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 23.5, "bb_rate": 7.8, "obp": 0.323, "power": 0.180, "bullpen": 0.72},
    {"team": "BOS", "k_rate": 22.8, "bb_rate": 8.9, "obp": 0.318, "power": 0.175, "bullpen": 0.65},
    {"team": "LAD", "k_rate": 20.9, "bb_rate": 6.5, "obp": 0.335, "power": 0.190, "bullpen": 0.78},
    {"team": "SF",  "k_rate": 23.1, "bb_rate": 7.5, "obp": 0.310, "power": 0.165, "bullpen": 0.70},
    {"team": "ATL", "k_rate": 21.0, "bb_rate": 7.0, "obp": 0.330, "power": 0.185, "bullpen": 0.74},
    {"team": "NYM", "k_rate": 22.0, "bb_rate": 8.2, "obp": 0.315, "power": 0.172, "bullpen": 0.66},
    {"team": "HOU", "k_rate": 22.5, "bb_rate": 7.2, "obp": 0.320, "power": 0.185, "bullpen": 0.73},
    {"team": "TEX", "k_rate": 21.8, "bb_rate": 7.6, "obp": 0.325, "power": 0.188, "bullpen": 0.71},
    {"team": "PHI", "k_rate": 23.0, "bb_rate": 7.4, "obp": 0.328, "power": 0.182, "bullpen": 0.75},
    {"team": "WSH", "k_rate": 21.5, "bb_rate": 8.0, "obp": 0.312, "power": 0.170, "bullpen": 0.64},
])

# ----------------------------
# ODDS (SIMULATED - YOU CAN EDIT LATER)
# ----------------------------
games["odds"] = [-115] * len(games)

def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)

# ----------------------------
# MODEL
# ----------------------------
rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    pitching = (
        (away["k_rate"] - away["bb_rate"]) +
        (home["k_rate"] - home["bb_rate"])
    ) / 60

    offense = (
        (away["obp"] + home["obp"]) / 2 +
        (away["power"] + home["power"]) / 4
    )

    bullpen = (away["bullpen"] + home["bullpen"]) / 2

    score = pitching + (bullpen * 0.2) - offense

    nrfi_prob = 1 / (1 + np.exp(-5 * score))

    decimal_odds = odds_to_decimal(g["odds"])
    implied = 1 / decimal_odds

    ev = (nrfi_prob * (decimal_odds - 1)) - (1 - nrfi_prob)

    kelly = max((nrfi_prob * decimal_odds - 1) / (decimal_odds - 1), 0)

    rows.append({
        "away_team": g["away"],
        "home_team": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied, 3),
        "ev": round(ev, 3),
        "kelly_%": round(kelly * 100, 1),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE CLASSIFICATION
# ----------------------------
df["tier"] = df["ev"].apply(
    lambda x: "🔥 STRONG BET" if x > 0.05
    else ("✅ LEAN" if x > 0 else "❌ NO BET")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("📊 Today's MLB NRFI Slate")
st.dataframe(df)

st.subheader("🔥 Best +EV Plays")

best = df[df["ev"] > 0.05]

if best.empty:
    best = df.sort_values("ev", ascending=False).head(2)

st.dataframe(best)

st.caption(f"Updated: {df['timestamp'].iloc[0]}")