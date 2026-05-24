import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "model1": 0.62,
            "model2": 0.70,
            "model3": 0.74,
            "timestamp": str(datetime.now())
        }
    ])

    df.to_csv("data/predictions.csv", index=False)

    print("PIPELINE RAN SUCCESSFULLY")

if __name__ == "__main__":
    run()