import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    # ----------------------------
    # SAMPLE MLB GAMES (expand later)
    # ----------------------------
    games = [
        {"away_team": "Yankees", "home_team": "Red Sox"},
        {"away_team": "Dodgers", "home_team": "Giants"},
        {"away_team": "Braves", "home_team": "Mets"},
    ]

    df = pd.DataFrame(games)

    # ----------------------------
    # TEMP NRFI MODEL (placeholder logic)
    # ----------------------------
    df["model1"] = 0.62
    df["model2"] = 0.70
    df["model3"] = 0.74

    # average probability estimate
    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    # ----------------------------
    # TIMESTAMP (local readable format)
    # ----------------------------
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # ----------------------------
    # SAVE OUTPUT FOR STREAMLIT
    # ----------------------------
    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE RAN SUCCESSFULLY")

if __name__ == "__main__":
    run()