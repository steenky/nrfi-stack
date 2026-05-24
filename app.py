import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

st.title("🏛️ LIVE NRFI QUANT DESK")

# =========================================================
# 1. LIVE SLATE LAYER (SIMULATED REAL MLB INPUT)
# =========================================================
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS", "odds": -120, "park": "Fenway"},
    {"away": "LAD", "home": "SF", "odds": -110, "park": "Oracle"},
    {"away": "ATL", "home": "NYM", "odds": -115, "park": "Citi Field"},
    {"away": "HOU", "home": "TEX", "odds": -112, "park": "Globe Life"},
    {"away": "PHI", "home": "WSH", "odds": -108, "park": "Nationals Park"},
])

# =========================================================
# 2. MARKET DATA LAYER (TEAM + PITCHER PROXY STACK)
# =========================================================
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 24.2, "bb_rate": 7.3, "obp": 0.324, "iso": 0.183, "bullpen": 0.74, "starter": 0.82},
    {"team": "BOS", "k_rate": 22.1, "bb_rate": 8.9, "obp": 0.316, "iso": 0.171, "bullpen": 0.66, "starter": 0.71},
    {"team": "LAD", "k_rate": 20.7, "bb_rate": 6.2, "obp": 0.337, "iso": 0.192, "bullpen": 0.81, "starter": 0.88},
    {"team": "SF",  "k_rate": 23.0, "bb_rate": 7.0, "obp": 0.309, "iso": 0.163, "bullpen": 0.72, "starter": 0.76},
    {"team": "ATL", "k_rate": 21.4, "bb_rate": 6.8, "obp": 0.331, "iso": 0.186, "bullpen": 0.75, "starter": 0.80},
    {"team": "NYM", "k_rate": 22.0, "bb_rate": 8.0, "obp": 0.314, "iso": 0.174, "bullpen": 0.67, "starter": 0.72},
    {"team": "HOU", "k_rate": 22.8, "bb_rate": 7.0, "obp": 0.322, "iso": 0.185, "bullpen": 0.76, "starter": 0.78},
    {"team": "TEX", "k_rate": 21.8, "bb_rate": 7.3, "obp": 0.325, "iso": 0.187, "bullpen": 0.72, "starter": 0.75},
    {"team": "PHI", "k_rate": 23.1, "bb_rate": 7.4, "obp": 0.328, "iso": 0.182, "bullpen": 0.75, "starter": 0.83},
    {"team": "WSH", "k_rate": 21.6, "bb_rate": 8.1, "obp": 0.312, "iso": 0.170, "bullpen": 0.64, "starter": 0.69},
])

# =========================================================
# 3. ODDS ENGINE
# =========================================================
def odds_to_decimal(o):
    return 1 + (100 / abs(o)) if o < 0 else 1 + (o / 100)

# =========================================================
# 4. FEATURE ENGINE (DESK-GRADE SIGNALS)
# =========================================================
def features(away, home):

    pitching = (
        (away["k_rate"] - away["bb_rate"]) +
        (home["k_rate"] - home["bb_rate"])
    ) / 60

    offense = (
        (away["obp"] + home["obp"]) / 2 * 0.6 +
        (away["iso"] + home["iso"]) / 4
    )

    bullpen = (away["bullpen"] + home["bullpen"]) / 2

    starter = (away["starter"] + home["starter"]) / 2

    return pitching, offense, bullpen, starter

# =========================================================
# 5. LIVE QUANT MODEL ENGINE
# =========================================================
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    pitching, offense, bullpen, starter = features(away, home)

    # =====================================================
    # CORE DESK SCORE (WEIGHTED FACTOR MODEL)
    # =====================================================
    score = (
        starter * 1.25 +
        pitching * 0.95 +
        bullpen * 0.35 -
        offense
    )

    nrfi_prob = sigmoid(6.9 * score)

    # MARKET PRICING
    decimal = odds_to_decimal(g["odds"])
    implied = 1 / decimal

    # EDGE METRICS
    edge = nrfi_prob - implied
    ev = (nrfi_prob * (decimal - 1)) - (1 - nrfi_prob)

    # KELLY (RISK CONTROL)
    kelly = max((nrfi_prob * decimal - 1) / (decimal - 1), 0)
    stake = kelly * 0.5

    # CLV EXPECTATION (DESK METRIC)
    clv = edge * 100

    # CONFIDENCE SCORE (MULTI FACTOR)
    confidence = (
        abs(edge) * 130 +
        nrfi_prob * 12 +
        starter * 15
    )

    rows.append({
        "away": g["away"],
        "home": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied, 3),
        "edge": round(edge, 3),
        "ev": round(ev, 3),
        "kelly_%": round(stake * 100, 2),
        "clv_expectation": round(clv, 2),
        "confidence": round(confidence, 2),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# =========================================================
# 6. DESK RATING SYSTEM
# =========================================================
def rating(row):
    if row["ev"] > 0.06 and row["edge"] > 0.03 and row["confidence"] > 8:
        return "🔥 A-PLAY (LIVE DESK)"
    elif row["ev"] > 0.02:
        return "✅ B-PLAY"
    else:
        return "❌ PASS"

df["rating"] = df.apply(rating, axis=1)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================================================
# 7. DESK LEDGER (REAL QUANT FEATURE)
# =========================================================
LOG_FILE = "live_quant_desk_log.csv"

if os.path.exists(LOG_FILE):
    history = pd.read_csv(LOG_FILE)
else:
    history = pd.DataFrame(columns=df.columns)

history = pd.concat([history, df], ignore_index=True)
history.to_csv(LOG_FILE, index=False)

# simulated pnl tracking
history["pnl"] = history.apply(
    lambda x: x["ev"] if "A-PLAY" in str(x["rating"]) else
              (x["ev"] * 0.5 if "B-PLAY" in str(x["rating"]) else 0),
    axis=1
)

total_pnl = history["pnl"].sum()
trades = len(history)
roi = total_pnl / trades if trades > 0 else 0

wins = (history["pnl"] > 0).sum()
win_rate = wins / trades if trades > 0 else 0

# =========================================================
# 8. OUTPUT DASHBOARD
# =========================================================
st.subheader("📊 Live Quant Desk Board")
st.dataframe(df)

st.subheader("🔥 A-Plays (Desk Approved)")
st.dataframe(df[df["rating"] == "🔥 A-PLAY (LIVE DESK)"])

st.subheader("📈 Desk Performance Metrics")

c1, c2, c3 = st.columns(3)
c1.metric("Signals", trades)
c2.metric("Simulated PnL", round(total_pnl, 3))
c3.metric("Win Rate", round(win_rate, 3))

st.subheader("📉 Execution Ledger (Last 10)")
st.dataframe(history.tail(10))

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")