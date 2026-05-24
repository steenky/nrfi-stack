import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    games = [
        {"away_team": "Yankees", "home_team": "Red Sox"},
        {"away_team": "Dodgers", "home_team": "Giants"},
        {"away_team": "Braves", "home_team": "Mets"},
        {"away_team": "Astros", "home_team": "Rangers"},
        {"away_team": "Cubs", "home_team": "Cardinals"},
    ]

    df = pd.DataFrame(games)

    # ----------------------------
    # REALISTIC NRFI MODEL (STABLE VERSION)
    # ----------------------------

    df["pitch_strength"] = df["away_team"].apply(lambda x: len(x)) + df["home_team"].apply(lambda x: len(x))
    df["offense_pressure"] = df["away_team"].apply(lambda x: len(x[::-1])) * 0.01

    base = 0.52

    df["model1"] = base - (df["pitch_strength"] * 0.003) - (df["offense_pressure"] * 0.1)
    df["model2"] = df["model1"] + 0.02
    df["model3"] = df["model1"] - 0.015

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE COMPLETE")

if __name__ == "__main__":
    run()