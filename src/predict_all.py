import pandas as pd
import os

def run():

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "model1": 0.62,
            "model2": 0.70,
            "model3": 0.74,
        },
        {
            "away_team": "Dodgers",
            "home_team": "Giants",
            "model1": 0.66,
            "model2": 0.71,
            "model3": 0.78,
        }
    ])

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    df.to_csv("data/predictions.csv", index=False)

if __name__ == "__main__":
    run()
