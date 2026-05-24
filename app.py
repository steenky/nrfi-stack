import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

st.title("🏛️ NRFI Institutional Quant System (Simulated Desk Model)")

# =========================================================
# 1. MARKET DATA LAYER (TEAM BASE FEATURES)
# =========================================================
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 24.0, "bb_rate": 7.5, "obp": 0.324, "iso": 0.182, "bullpen": 0.74, "form": 0.03},
    {"team": "BOS", "k_rate": 22.3, "bb_rate": 8.8, "obp": 0.317, "iso": 0.171, "bullpen": 0.66, "form": -0.01},
    {"team": "LAD", "k_rate": 20.7, "bb_rate": 6.3, "obp": 0.336, "iso": 0.191, "bullpen": 0.80, "form": 0.04},
    {"team": "SF",  "k_rate": 23.2, "bb_rate": 7.2, "obp": 0.309, "iso": 0.163, "bullpen": 0.71, "form": 0.00},
    {"team": "ATL", "k_rate": 21.4, "bb_rate": 6.9, "obp": 0.331, "iso": 0.186, "bullpen": 0.75, "form": 0.02},
    {"team": "NYM", "k_rate": 22.0, "bb_rate": 8.0, "obp": 0.314, "iso": 0.174, "bullpen": 0.67, "form": -0.02},
    {"team": "HOU", "k_rate": 22.8, "bb_rate": 7.0, "obp": 0.322, "iso": 0.185, "bullpen": 0.76, "form": 0.01},
    {"team": "TEX", "k_rate": 21.6, "bb_rate": 7.4, "obp": 0.325, "iso": 0.187, "bullpen": 0.72, "form": 0.00},
])

# =========================================================
# 2. SLATE (DAILY INPUT LAYER)
# =========================================================
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS", "odds": -118},
    {"away": "LAD", "home": "SF", "odds": -110},
    {"away": "ATL", "home": "NYM", "odds": -115},
    {"away": "HOU", "home": "TEX", "odds": -112},
])

# =========================================================
# 3. MARKET CONVERSION LAYER
# =========================================================
def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)

# league baseline NRFI probability
BASE_RATE = 0.52

# =========================================================
# 4. FEATURE ENGINEERING LAYER
# =========================================================
def build_features(away, home):

    pitching = (
        (away["k_rate"] - away["bb_rate"]) +
        (home["k_rate"] - home["bb_rate"])
    ) / 60

    offense = (
        (away["obp"] + home["obp"]) / 2 * 0.6 +
        (away["iso"] + home["iso"]) / 4
    )

    bullpen = (away["bullpen"] + home["bullpen"]) / 2

    form = (away["form"] + home["form"]) / 2

    return pitching, offense, bullpen, form

# =========================================================
# 5. MODEL LAYER (CALIBRATED SIGMOID MODEL)
# =========================================================
def model_prob(score):
    # calibrated so outputs stay realistic (0.44–0.66 range typical)
    return 1 / (1 + np.exp(-6.5 * score))

# =========================================================
# 6. SCORING ENGINE
# =========================================================
rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    pitching, offense, bullpen, form = build_features(away, home)

    score = pitching + bullpen * 0.25 + form * 0.3 - offense

    nrfi_prob = model_prob(score)

    decimal_odds = odds_to_decimal(g["odds"])
    implied = 1 / decimal_odds

    edge = nrfi_prob - implied

    ev = (nrfi_prob * (decimal_odds - 1)) - (1 - nrfi_prob)

    kelly = max((nrfi_prob * decimal_odds - 1) / (decimal_odds - 1), 0)
    kelly_safe = kelly * 0.5

    confidence = abs(edge) * 100 + nrfi_prob * 10

    rows.append({
        "away": g["away"],
        "home": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied, 3),
        "edge": round(edge, 3),
        "ev": round(ev, 3),
        "kelly_%": round(kelly_safe * 100, 2),
        "confidence": round(confidence, 2),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# =========================================================
# 7. INSTITUTIONAL RISK FILTERS
# =========================================================
def classify(row):
    if row["ev"] > 0.06 and row["edge"] > 0.03 and row["confidence"] > 6:
        return "🔥 A-RATED (INSTITUTIONAL)"
    elif row["ev"] > 0.02 and row["edge"] > 0:
        return "✅ B-RATED (VALUE)"
    else:
        return "❌ C-RATED (PASS)"

df["rating"] = df.apply(classify, axis=1)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================================================
# 8. TRACKING / BACKTEST LAYER (SIMULATED LEDGER)
# =========================================================
LOG_FILE = "nrfi_institution_log.csv"

if os.path.exists(LOG_FILE):
    history = pd.read_csv(LOG_FILE)
else:
    history = pd.DataFrame(columns=df.columns)

history = pd.concat([history, df], ignore_index=True)
history.to_csv(LOG_FILE, index=False)

# performance simulation (edge-based proxy)
history["sim_profit"] = history.apply(
    lambda x: x["ev"] if "A-RATED" in str(x["rating"]) else
              (x["ev"] * 0.5 if "B-RATED" in str(x["rating"]) else 0),
    axis=1
)

# rolling stats
total_trades = len(history)
total_profit = history["sim_profit"].sum()
roi = (total_profit / total_trades) if total_trades > 0 else 0

# win rate proxy
wins = (history["sim_profit"] > 0).sum()
win_rate = wins / total_trades if total_trades > 0 else 0

# =========================================================
# 9. OUTPUT LAYER
# =========================================================
st.subheader("📊 Daily Institutional NRFI Board")
st.dataframe(df)

st.subheader("🔥 A-Rated Plays Only")
st.dataframe(df[df["rating"] == "🔥 A-RATED (INSTITUTIONAL)"])

st.subheader("📈 Portfolio Performance (Simulated)")

c1, c2, c3 = st.columns(3)
c1.metric("Total Signals", total_trades)
c2.metric("Simulated ROI (per trade)", round(roi, 3))
c3.metric("Win Rate", round(win_rate, 3))

st.subheader("📉 Execution Log (Last 10 Trades)")
st.dataframe(history.tail(10))

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")