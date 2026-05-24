import streamlit as st
import pandas as pd
from datetime import datetime
from mlbstatsapi import MLBStatsAPI

st.title("⚾ NRFI Predictor (Stable MLB API)")

api = MLBStatsAPI()

# ----------------------------
# GET TEAM PITCHING STATS
# ----------------------------
teams = api.get_teams()

rows = []

for team in teams[:10]:  # limit for speed/stability
    try:
        stats = api.get_team_stats(team.id, "pitching")

        rows.append({
            "team": team.name,
            "whip": stats.get("whip", 1.30),
            "k9": stats.get("strikeoutsPer9Inn", 8.5),
            "bb9": stats.get("walksPer9Inn", 3.2),
            "hr9": stats.get("homeRunsPer9", 1.1),
        })
    except:
        continue

df = pd.DataFrame(rows)

# ----------------------------
# NRFI MODEL
# ----------------------------
df["nrfi_score"] = (
    df["k9"] * 0.35
    - df["bb9"] * 0.25
    - df["hr9"] * 0.35
    - df["whip"] * 0.10
)

df["edge_tier"] = df["nrfi_score"].apply(
    lambda x: "🔥 STRONG NRFI" if x > 3.0
    else ("✅ LEAN NRFI" if x > 2.0 else "PASS")
)

df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("Team Pitching NRFI Ratings")
st.dataframe(df.sort_values("nrfi_score", ascending=False))

st.subheader("🔥 Best NRFI Teams")
st.dataframe(df[df["edge_tier"] == "🔥 STRONG NRFI"])

st.caption(f"Last Updated: {df['timestamp'].iloc[0]}")