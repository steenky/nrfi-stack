import pandas as pd
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    # ----------------------------
    # SAMPLE MLB SLATE (same structure as before)
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
    # REALISTIC MLB FEATURES (SIMULATED FOR NOW)
    # Later we replace these with real API data
    # ----------------------------

    pitcher_whip = {
        "Yankees": 1.18, "Red Sox": 1.25,
        "Dodgers": 1.10, "Giants": 1.20,
        "Braves": 1.15, "Mets": 1.22,
        "Astros": 1.12, "Rangers": 1.30,
        "Cubs": 1.28, "Cardinals": 1.19
    }

    lineup_obp = {
        "Yankees": 0.330, "Red Sox": 0.320,
        "Dodgers": 0.340, "Giants": 0.315,
        "Braves": 0.335, "Mets": 0.310,
        "Astros": 0.325, "Rangers": 0.318,
        "Cubs": 0.312, "Cardinals": 0.321
    }

    park_factor = {
        "Yankees": 1.02, "Red Sox": 1.05,
        "Dodgers": 0.98, "Giants": 0.94,
        "Braves": 1.01, "Mets": 0.97,
        "Astros": 1.03, "Rangers": 1.08,
        "Cubs": 1.00, "Cardinals": 0.99
    }

    # ----------------------------
    # FEATURE ENGINEERING
    # ----------------------------

    def get_features(row):
        away = row["away_team"]
        home = row["home_team"]

        # pitching advantage (lower WHIP = better for NRFI)
        pitcher_score = (
            pitcher_whip.get(away, 1.25) +
            pitcher_whip.get(home, 1.25)
        )

        # offense pressure (higher OBP = worse for NRFI)
        offense_score = (
            lineup_obp.get(away, 0.320) +
            lineup_obp.get(home, 0.320)
        )

        # park environment (higher = more runs)
        park_score = (
            park_factor.get(away, 1.00) +
            park_factor.get(home, 1.00)
        )

        return pitcher_score, offense_score, park_score

    features = df.apply(get_features, axis=1, result_type="expand")
    features.columns = ["pitcher_score", "offense_score", "park_score"]

    df = pd.concat([df, features], axis=1)

    # ----------------------------
    # NRFI MODEL (REALISTIC WEIGHTED LOGIC)
    # ----------------------------

    base = 0.52

    df["model1"] = (
        base
        - (df["pitcher_score"] - 2.30) * 0.20
        - (df["offense_score"] - 0.64) * 0.80
        - (df["park_score"] - 2.00) * 0.10
    )

    df["model2"] = df["model1"] + 0.02
    df["model3"] = df["model1"] - 0.015

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    # ----------------------------
    # TIMESTAMP
    # ----------------------------
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # ----------------------------
    # SAVE OUTPUT
    # ----------------------------
    df.to_csv("data/predictions.csv", index=False)

    print("OPTION A PIPELINE COMPLETE")

if __name__ == "__main__":
    run()