import pandas as pd
import numpy as np
import os
from datetime import datetime

print("RUNNING NEW B3-B FILE")

def run():

    os.makedirs("data", exist_ok=True)

    games = [
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "away_pitcher": "Cole",
            "home_pitcher": "Bello"
        },
        {
            "away_team": "Dodgers",
            "home_team": "Giants",
            "away_pitcher": "Yamamoto",
            "home_pitcher": "Webb"
        },
        {
            "away_team": "Braves",
            "home_team": "Mets",
            "away_pitcher": "Strider",
            "home_pitcher": "Senga"
        },
        {
            "away_team": "Astros",
            "home_team": "Rangers",
            "away_pitcher": "Valdez",
            "home_pitcher": "Eovaldi"
        },
        {
            "away_team": "Cubs",
            "home_team": "Cardinals",
            "away_pitcher": "Steele",
            "home_pitcher": "Gray"
        }
    ]

    df = pd.DataFrame(games)

    pitcher_metrics = {

        "Cole": {
            "whip": 1.05,
            "k9": 10.8,
            "bb9": 2.1,
            "hr9": 0.8
        },

        "Bello": {
            "whip": 1.31,
            "k9": 8.2,
            "bb9": 3.3,
            "hr9": 1.1
        },

        "Yamamoto": {
            "whip": 1.02,
            "k9": 10.4,
            "bb9": 2.0,
            "hr9": 0.7
        },

        "Webb": {
            "whip": 1.15,
            "k9": 8.5,
            "bb9": 1.9,
            "hr9": 0.9
        },

        "Strider": {
            "whip": 1.09,
            "k9": 13.2,
            "bb9": 2.8,
            "hr9": 0.9
        },

        "Senga": {
            "whip": 1.20,
            "k9": 10.1,
            "bb9": 3.4,
            "hr9": 0.8
        },

        "Valdez": {
            "whip": 1.14,
            "k9": 9.1,
            "bb9": 2.9,
            "hr9": 0.7
        },

        "Eovaldi": {
            "whip": 1.18,
            "k9": 8.9,
            "bb9": 2.2,
            "hr9": 1.0
        },

        "Steele": {
            "whip": 1.16,
            "k9": 9.4,
            "bb9": 2.5,
            "hr9": 0.8
        },

        "Gray": {
            "whip": 1.21,
            "k9": 9.0,
            "bb9": 2.7,
            "hr9": 0.9
        },
    }

    offense_metrics = {

        "Yankees": {
            "obp": 0.334,
            "k_rate": 0.238
        },

        "Red Sox": {
            "obp": 0.321,
            "k_rate": 0.241
        },

        "Dodgers": {
            "obp": 0.346,
            "k_rate": 0.212
        },

        "Giants": {
            "obp": 0.314,
            "k_rate": 0.249
        },

        "Braves": {
            "obp": 0.337,
            "k_rate": 0.227
        },

        "Mets": {
            "obp": 0.312,
            "k_rate": 0.253
        },

        "Astros": {
            "obp": 0.326,
            "k_rate": 0.231
        },

        "Rangers": {
            "obp": 0.319,
            "k_rate": 0.246
        },

        "Cubs": {
            "obp": 0.313,
            "k_rate": 0.251
        },

        "Cardinals": {
            "obp": 0.322,
            "k_rate": 0.239
        },
    }

    park_factor = {
        "Red Sox": 1.05,
        "Giants": 0.94,
        "Mets": 0.97,
        "Rangers": 1.08,
        "Cardinals": 0.99
    }

    def build_features(row):

        away_pitch = pitcher_metrics[row["away_pitcher"]]
        home_pitch = pitcher_metrics[row["home_pitcher"]]

        away_off = offense_metrics[row["away_team"]]
        home_off = offense_metrics[row["home_team"]]

        park = park_factor.get(row["home_team"], 1.00)

        return pd.Series({

            "combined_whip":
                away_pitch["whip"] + home_pitch["whip"],

            "combined_k9":
                away_pitch["k9"] + home_pitch["k9"],

            "combined_bb9":
                away_pitch["bb9"] + home_pitch["bb9"],

            "combined_hr9":
                away_pitch["hr9"] + home_pitch["hr9"],

            "combined_obp":
                away_off["obp"] + home_off["obp"],

            "combined_k_rate":
                away_off["k_rate"] + home_off["k_rate"],

            "park_factor":
                park
        })

    features = df.apply(build_features, axis=1)

    df = pd.concat([df, features], axis=1)

    base = 0.52

    df["model1"] = (
        base
        - (df["combined_whip"] - 2.30) * 0.28
        + (df["combined_k9"] - 18.0) * 0.012
        - (df["combined_bb9"] - 5.2) * 0.020
        - (df["combined_hr9"] - 1.8) * 0.045
        - (df["combined_obp"] - 0.64) * 0.90
        + (df["combined_k_rate"] - 0.48) * 0.65
        - (df["park_factor"] - 1.00) * 0.12
    )

    df["model2"] = df["model1"] + 0.012
    df["model3"] = df["model1"] - 0.009

    df["avg_nrfi"] = (
        df[["model1", "model2", "model3"]]
        .mean(axis=1)
        .clip(0.01, 0.99)
    )

    conditions = [
        df["avg_nrfi"] >= 0.58,
        df["avg_nrfi"] >= 0.54,
    ]

    labels = [
        "🔥 STRONG NRFI",
        "✅ LEAN NRFI"
    ]

    df["edge_tier"] = np.select(
        conditions,
        labels,
        default="PASS"
    )

    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    df = df.sort_values(
        by="avg_nrfi",
        ascending=False
    )

    df.to_csv(
        "data/predictions.csv",
        index=False
    )

    print("B3-B MODEL COMPLETE")

if __name__ == "__main__":
    run()