
import pandas as pd
import os

def run():

    os.makedirs("data", exist_ok=True)

    # TEMP STRUCTURE — this is where real MLB data will plug in next step
    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",

            # pitching (placeholder but structured correctly)
            "away_sp_whip": 1.25,
            "home_sp_whip": 1.30,

            "away_k_rate": 0.24,
            "home_k_rate": 0.22,

            # lineup strength
            "away_top3_obp": 0.340,
            "home_top3_obp": 0.330,

            # park factor
            "park_factor": 1.05
        },
        {
            "away_team": "Dodgers",
            "home_team": "Giants",

            "away_sp_whip": 1.10,
            "home_sp_whip": 1.18,

            "away_k_rate": 0.27,
            "home_k_rate": 0.25,

            "away_top3_obp": 0.350,
            "home_top3_obp": 0.320,

            "park_factor": 0.95
        }
    ])

    # SIMPLE REAL MODEL (not fake random anymore)
    df["model1"] = (
        0.5
        - (df["away_sp_whip"] * 0.10)
        - (df["home_sp_whip"] * 0.10)
        - (df["away_top3_obp"] * 0.20)
        - (df["home_top3_obp"] * 0.20)
        + (df["park_factor"] * 0.05)
    )

    df["model2"] = df["model1"] + 0.05  # placeholder for XGBoost later
    df["model3"] = df["model1"] - 0.03  # volatility model

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    df.to_csv("data/predictions.csv", index=False)

if __name__ == "__main__":
    run()
