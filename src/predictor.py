import pandas as pd
import numpy as np
import os
from datetime import datetime

def run():

    print("PIPELINE STARTED")

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "away_pitcher": "Cole",
            "home_pitcher": "Bello"
        }
    ])

    df["avg_nrfi"] = 0.62
    df["edge_tier"] = "🔥 STRONG NRFI"
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE COMPLETE")

if __name__ == "__main__":
    run()