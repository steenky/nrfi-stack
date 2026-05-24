import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    print("RUNNING PIPELINE...")

    games = [
        {"away_team": "Yankees", "home_team": "Red Sox"},
        {"away_team": "Dodgers", "home_team": "Giants"},
        {"away_team": "Braves", "home_team": "Mets"},
        {"away_team": "Astros", "home_team": "Rangers"},
        {"away_team": "Cubs", "home_team": "Cardinals"},
    ]

    df = pd.DataFrame(games)

    print("Games loaded:", len(df))

    # make values clearly different so we KNOW it updated
    df["model1"] = [0.60, 0.62, 0.64, 0.66, 0.68]
    df["model2"] = [0.65, 0.67, 0.69, 0.71, 0.73]
    df["model3"] = [0.70, 0.72, 0.74, 0.76, 0.78]

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    print(df)

    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE COMPLETE - FILE WRITTEN")

if __name__ == "__main__":
    run()