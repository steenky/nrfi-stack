import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pybaseball import pitching_stats, batting_stats

st.title("⚾ NRFI Edge Model (Real Data Version)")

# ----------------------------
# LOAD DATA (CACHED FOR SPEED)
# ----------------------------
@st.cache_data(ttl=86400)
def load_data():
    pitchers = pitching_stats(2025)
    batters = batting_stats(2025)
    return pitchers, batters

pitchers, batters = load_data()

# ----------------------------
# PITCHER METRICS
# ----------------------------
pitchers = pitchers[["Name", "Team", "K%", "BB%", "HR/9"]].dropna()
pitchers.columns = ["pitcher", "team", "k_rate", "bb_rate", "hr9"]

# convert percent strings if needed
for col in ["k_rate", "bb_rate"]:
    pitchers[col] = pitchers[col].astype(str).str.replace("%", "").astype(float)

# ----------------------------
# OFFENSE METRICS
# ----------------------------
batters = batters[["Team", "K%", "OBP"]].dropna()
batters.columns = ["team", "off_k", "obp"]

batters["off_k"] = batters["off_k"].astype(str).str.replace("%", "").astype(float)

# ----------------------------
# BUILD MATCHUPS (SIMPLIFIED SLATE)
# ----------------------------
sample_games = pd.DataFrame([
    {"away_team": "NYY", "home_team": "BOS"},
    {"away_team": "LAD", "home_team": "SF"},
    {"away_team": "ATL", "home_team": "NYM"},
    {"away_team": "HOU", "home_team": "TEX"},
    {"away_team": "PHI", "home_team": "WSH"},
])

def get_pitcher(team):
    p = pitchers[pitchers["team"] == team]
    return p.iloc[0] if len(p) > 0 else None

def get_offense(team):
    o = batters[batters["team"] == team]
    return o.iloc[0] if len(o) > 0 else None

rows = []

for _, g in sample_games.iterrows():

    away_p = get_pitcher(g["away_team"])
    home_p = get_pitcher(g["home_team"])
    away_o = get_offense(g["away_team"])
    home_o = get_offense(g["home_team"])

    if away_p is None or home_p is None:
        continue

    # ----------------------------
    # NRFI LOGIC (FIRST INNING MODEL)
    # ----------------------------
    pitcher_score = (
        (away_p["k_rate"] + home_p["k_rate"]) * 0.4
        - (away_p["bb_rate"] + home_p["bb_rate"]) * 0.3
        - (away_p["hr9"] + home_p["hr9"]) * 0.3
    )

    offense_risk = 0
    if away_o is not None:
        offense_risk += away_o["obp"] + away_o["off_k"] * 0.2
    if home_o is not None:
        offense_risk += home_o["obp"] + home_o["off_k"] * 0.2

    nrfi_prob = 1 / (1 + np.exp(-(pitcher_score - offense_risk)))

    rows.append({
        "away_team": g["away_team"],
        "home_team": g["home_team"],
        "nrfi_prob": round(nrfi_prob, 3),
        "pitcher_score": round(pitcher_score, 3),
        "offense_risk": round(offense_risk, 3),
    })

df = pd.DataFrame(rows)

# ----------------------------
# EDGE TIERS
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