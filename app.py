import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

st.title("⚾ NRFI Quant Sharp System")

# =========================================================
# 1. TEAM DATA (STATIC FACTOR BASES)
# =========================================================
teams = pd.DataFrame([
    {"team": "NYY", "k_rate": 23.8, "bb_rate": 7.6, "obp": 0.324, "iso": 0.182, "bullpen": 0.73},
    {"team": "BOS", "k_rate": 22.4, "bb_rate": 8.7, "obp": 0.317, "iso": 0.171, "bullpen": 0.66},
    {"team": "LAD", "k_rate": 20.8, "bb_rate": 6.4, "obp": 0.336, "iso": 0.191, "bullpen": 0.79},
    {"team": "SF",  "k_rate": 23.0, "bb_rate": 7.3, "obp": 0.309, "iso": 0.163, "bullpen": 0.71},
    {"team": "ATL", "k_rate": 21.2, "bb_rate": 6.9, "obp": 0.331, "iso": 0.186, "bullpen": 0.74},
    {"team": "NYM", "k_rate": 22.1, "bb_rate": 8.1, "obp": 0.314, "iso": 0.174, "bullpen": 0.67},
    {"team": "HOU", "k_rate": 22.6, "bb_rate": 7.1, "obp": 0.322, "iso": 0.185, "bullpen": 0.75},
    {"team": "TEX", "k_rate": 21.7, "bb_rate": 7.5, "obp": 0.325, "iso": 0.187, "bullpen": 0.72},
])

# =========================================================
# 2. SLATE (STATIC SAFE VERSION)
# =========================================================
games = pd.DataFrame([
    {"away": "NYY", "home": "BOS", "odds": -118},
    {"away": "LAD", "home": "SF", "odds": -110},
    {"away": "ATL", "home": "NYM", "odds": -115},
    {"away": "HOU", "home": "TEX", "odds": -112},
])

# =========================================================
# 3. ODDS CONVERSION
# =========================================================
def odds_to_decimal(odds):
    if odds < 0:
        return 1 + (100 / abs(odds))
    return 1 + (odds / 100)

# =========================================================
# 4. QUANT MODEL ENGINE
# =========================================================
rows = []

for _, g in games.iterrows():

    away = teams[teams["team"] == g["away"]].iloc[0]
    home = teams[teams["team"] == g["home"]].iloc[0]

    # -------------------------
    # PITCHING COMPONENT (K-BB Z SCORE STYLE)
    # -------------------------
    away_pitch = (away["k_rate"] - away["bb_rate"]) / 30
    home_pitch = (home["k_rate"] - home["bb_rate"]) / 30

    pitching = (away_pitch + home_pitch) / 2

    # -------------------------
    # OFFENSE COMPONENT (CONTACT + POWER)
    # -------------------------
    offense = (
        (away["obp"] + home["obp"]) / 2 * 0.6 +
        (away["iso"] + home["iso"]) / 4
    )

    # -------------------------
    # BULLPEN REGIME FACTOR
    # -------------------------
    bullpen = (away["bullpen"] + home["bullpen"]) / 2

    # -------------------------
    # FINAL RAW EDGE SCORE
    # -------------------------
    raw = pitching + bullpen * 0.25 - offense

    # CALIBRATED PROBABILITY (QUANT CALIBRATION CURVE)
    nrfi_prob = 1 / (1 + np.exp(-7.5 * raw))

    # -------------------------
    # MARKET
    # -------------------------
    decimal = odds_to_decimal(g["odds"])
    implied = 1 / decimal

    edge = nrfi_prob - implied

    ev = (nrfi_prob * (decimal - 1)) - (1 - nrfi_prob)

    kelly = max((nrfi_prob * decimal - 1) / (decimal - 1), 0)

    # -------------------------
    # CONFIDENCE (VOLATILITY ADJUSTED EDGE)
    # -------------------------
    confidence = abs(edge) * (nrfi_prob * 100)

    rows.append({
        "away": g["away"],
        "home": g["home"],
        "nrfi_prob": round(nrfi_prob, 3),
        "implied_prob": round(implied, 3),
        "edge": round(edge, 3),
        "ev": round(ev, 3),
        "kelly_%": round(kelly * 100, 2),
        "confidence": round(confidence, 2),
        "odds": g["odds"]
    })

df = pd.DataFrame(rows)

# =========================================================
# 5. SIGNAL CLASSIFICATION
# =========================================================
def classify(row):
    if row["ev"] > 0.06 and row["edge"] > 0.03:
        return "🔥 SHARP +EV"
    elif row["ev"] > 0.02:
        return "✅ VALUE"
    else:
        return "❌ NO BET"

df["tier"] = df.apply(classify, axis=1)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================================================
# 6. QUANT TRACKING ENGINE (NEW)
# =========================================================
LOG_FILE = "nrfi_signal_log.csv"

if os.path.exists(LOG_FILE):
    history = pd.read_csv(LOG_FILE)
else:
    history = pd.DataFrame(columns=df.columns)

# append today's signals
history = pd.concat([history, df], ignore_index=True)
history.to_csv(LOG_FILE, index=False)

# performance simulation (VERY BASIC EDGE TEST)
history["profit_unit"] = history.apply(
    lambda x: x["ev"] if x["tier"] == "🔥 SHARP +EV" else 0,
    axis=1
)

# rolling performance
total_signals = len(history)
total_ev = history["profit_unit"].sum()

# =========================================================
# 7. DISPLAY
# =========================================================
st.subheader("📊 Today's Quant NRFI Slate")
st.dataframe(df)

st.subheader("🔥 Sharp Plays")
st.dataframe(df[df["tier"] == "🔥 SHARP +EV"])

st.subheader("📈 Model Performance (Simulated)")

col1, col2 = st.columns(2)
col1.metric("Total Signals Logged", total_signals)
col2.metric("Cumulative EV (Units)", round(total_ev, 2))

st.subheader("📉 Full History (Last 10)")
st.dataframe(history.tail(10))

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")