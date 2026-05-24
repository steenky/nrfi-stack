import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    # ----------------------------
    # SAMPLE MLB GAMES (replace later with real schedule API)
    # ----------------------------
    games = [
        {"away_team": "Yankees", "home_team": "Red Sox"},
        {"away_team": "Dodgers", "home_team": "Giants"},
        {"away_team": "Braves", "home_team": "Mets"},
        {"away_team": "Astros", "home_team": "Rangers"},
        {"away_team": "Cubs", "home_team": "Cardinals"},
    ]

    df = pd.DataFrame(games)

    # ----------------------------
    # NRFI MODEL (UPGRADED LOGIC)
    # ----------------------------

    # simple feature engineering
    df["away_strength"] = df["away_team"].apply(lambda x: len(x))
    df["home_strength"] = df["home_team"].apply(lambda x: len(x))

    base = 0.52  # league baseline NRFI probability

    df["model1"] = (
        base
        - (df["away_strength"] * 0.002)
        - (df["home_strength"] * 0.002)
    )

    df["model2"] = (
        base
        - (df["away_strength"] * 0.0015)
        - (df["home_strength"] * 0.0015)
        + 0.02
    )

    df["model3"] = (
        base
        - (df["away_strength"] * 0.0025)
        - (df["home_strength"] * 0.0025)
        - 0.01
    )

    # final blended probability
    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    # ----------------------------
    # TIMESTAMP (LOCAL READABLE)
    # ----------------------------
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # ----------------------------
    # SAVE OUTPUT FOR STREAMLIT
    # ----------------------------
    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE COMPLETE - NRFI DATA UPDATED")

if __name__ == "__main__":
    run()