import streamlit as st
import pandas as pd
from datetime import datetime

st.title("NRFI Predictor (STABLE VERSION)")

def generate_data():

    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "away_pitcher": "Cole",
            "home_pitcher": "Bello",
            "avg_nrfi": 0.62,
            "edge_tier": "🔥 STRONG NRFI",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "away_team": "Dodgers",
            "home_team": "Giants",
            "away_pitcher": "Yamamoto",
            "home_pitcher": "Webb",
            "avg_nrfi": 0.55,
            "edge_tier": "PASS",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ])

    return df

df = generate_data()

st.subheader("All Games")
st.dataframe(df)

st.subheader("Best Plays")
st.dataframe(df[df["edge_tier"] == "🔥 STRONG NRFI"])