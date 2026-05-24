import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

st.title("🏛️ NRFI EDGE DESK (Pro Betting System)")

# =========================================================
# 1. MARKET DATA (SIMULATED “LIVE” TEAM PROFILE LAYER)
# =========================================================
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 24.1, "bb_rate": 7.4, "obp": 0.324, "iso": 0.183, "bullpen": 0.74, "starter_k": 26.0},
    {"team": "BOS", "k_rate": 22.2, "bb_rate": 8.9, "obp": 0.316, "iso": 0.171, "bullpen": 0.66, "starter_k": 22.5},
    {"team": "LAD", "k_rate": 20.6, "bb_rate": 6.2, "obp": 0.337, "iso": 0.192, "bullpen": 0.81, "starter_k": 28.0},
    {"team": "SF",  "k_rate": 23.0, "bb_rate": 7.1, "obp": 0.309, "iso": 0.163, "bullpen": 0.71, "starter_k": 24.0},
    {"team": "ATL", "k_rate": 21.5, "bb_rate": 6.8, "obp": 0.331, "iso": 0.186, "bullpen": 0.75, "starter_k": 25.0},
    {"team": "NYM", "k_rate": 22.0, "bb_rate": 8.0, "obp": 0.314, "iso": 0.174, "bullpen": 0.67, "starter_k": 23.5},
    {"team": "HOU", "k_rate": 22.7, "bb_rate": 7.0, "obp": 0.322, "iso": 0.185, "bullpen": 0.76, "starter_k": 24.5},
    {"team": "TEX", "k_rate": 21.8, "bb_rate": 7.3, "obp": 0.325, "iso": 0.187, "bullpen": 0.72, "starter_k": 23.0},
])

# =========================================================
# 2. SLATE (EDGE DESK INPUT)
# =========================================================
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS", "odds": -118},
    {"away": "LAD", "home": "SF", "odds": -110},
    {"away": "ATL", "home": "NYM", "odds": -115},
    {"away": "HOU", "home": "TEX", "odds": -112},
])

# =========================================================
# 3. ODDS ENGINE (MARKET PRICING)
# =========================================================
def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)

# =========================================================
# 4. EDGE DESK FEATURE ENGINE
# =========================================================
def build_features(away, home):

    # Starter dominance (NEW: key upgrade)
    starter = (away["starter_k"] + home["starter_k"]) / 2 / 30

    # Team K-BB profile
    pitching = (
        (away["k_rate"] - away["bb_rate"]) +
        (home["k_rate"] - home["bb_rate"])
    ) / 60

    # First inning offense pressure
    offense = (
        (away["obp"] + home["obp"]) / 2 * 0.6 +
        (away["iso"] + home["iso"]) / 4
    )

    # Bullpen support
    bullpen = (away["bullpen"] + home["bullpen"]) / 2

    return starter, pitching, offense, bullpen

# =========================================================
# 5. EDGE DESK MODEL
# =========================================================
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    starter, pitching, offense, bullpen = build_features(away, home)

    # =====================================================
    # CORE EDGE FORMULA (DESK VERSION)
    # =====================================================
    score = (
        starter * 1.2 +
        pitching * 0.9 +
        bullpen * 0.3 -
        offense
    )

    nrfi_prob = sigmoid(6.8 * score)

    # MARKET PRICING
    decimal_odds = odds_to_decimal(g["odds"])
    implied = 1 / decimal_odds

    # EDGE METRICS
    edge = nrfi_prob - implied
    ev = (nrfi_prob * (decimal_odds - 1)) - (1 - nrfi_prob)

    # CLV EXPECTATION (proxy)
    clv_expectation = edge * 100

    # KELLY POSITION SIZING
    kelly = max((nrfi_prob * decimal_odds - 1) / (decimal_odds - 1), 0)
    stake = kelly * 0.5  # desk-safe fractional Kelly

    # CONFIDENCE (multi-factor weighting)
    confidence = (
        abs(edge) * 120 +
        nrfi_prob * 15 +
        starter * 10
    )

    rows.append({
        "away": g["away"],
        "home": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied, 3),
        "edge": round(edge, 3),
        "ev": round(ev, 3),
        "kelly_%": round(stake * 100, 2),
        "clv_expectation": round(clv_expectation, 2),
        "confidence": round(confidence, 2),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# =========================================================
# 6. DESK RATING SYSTEM
# =========================================================
def rating(row):
    if row["ev"] > 0.06 and row["edge"] > 0.03 and row["confidence"] > 8:
        return "🔥 A-PLAY (DESK APPROVED)"
    elif row["ev"] > 0.02:
        return "✅ B-PLAY (WATCHLIST)"
    else:
        return "❌ NO BET"

df["rating"] = df.apply(rating, axis=1)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================================================
# 7. DESK LEDGER (TRACKING + PERFORMANCE)
# =========================================================
LOG = "edge_desk_log.csv"

if os.path.exists(LOG):
    history = pd.read_csv(LOG)
else:
    history = pd.DataFrame(columns=df.columns)

history = pd.concat([history, df], ignore_index=True)
history.to_csv(LOG, index=False)

# simulated pnl
history["pnl"] = history.apply(
    lambda x: x["ev"] if "A-PLAY" in str(x["rating"]) else
              (x["ev"] * 0.5 if "B-PLAY" in str(x["rating"]) else 0),
    axis=1
)

total_pnl = history["pnl"].sum()
trades = len(history)
roi = total_pnl / trades if trades > 0 else 0

# =========================================================
# 8. OUTPUT DASHBOARD
# =========================================================
st.subheader("📊 Edge Desk Board")
st.dataframe(df)

st.subheader("🔥 A-Plays Only")
st.dataframe(df[df["rating"] == "🔥 A-PLAY (DESK APPROVED)"])

st.subheader("📈 Desk Performance")

c1, c2, c3 = st.columns(3)
c1.metric("Total Signals", trades)
c2.metric("Simulated PnL", round(total_pnl, 3))
c3.metric("ROI / Signal", round(roi, 4))

st.subheader("📉 Desk Ledger (Last 10)")
st.dataframe(history.tail(10))

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")