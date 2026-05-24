import pandas as pd
import os

def run():

    os.makedirs("data", exist_ok=True)

    # placeholder structure (ONLY used until MLB data is plugged in)
    games = [
        {"away_team": "Yankees", "home_team": "Red Sox"},
        {"away_team": "Dodgers", "home_team": "Giants"},
        {"away_team": "Braves", "home_team": "Mets"},
    ]

    df = pd.DataFrame(games)

    # fake model outputs (we will replace with real model next)
    df["model1"] = [0.62, 0.66, 0.71]
    df["model2"] = [0.70, 0.71, 0.75]
    df["model3"] = [0.74, 0.78, 0.80]

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    df.to_csv("data/predictions.csv", index=False)

if __name__ == "__main__":
    run()
