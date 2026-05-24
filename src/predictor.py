import pandas as pd
import os
from datetime import datetime

def run():

    print("PIPELINE START")

    os.makedirs("data", exist_ok=True)

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

    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE COMPLETE")
    print(df.columns.tolist())

if __name__ == "__main__":
    run()