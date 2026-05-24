import pandas as pd
import numpy as np
import os
from datetime import datetime

def run():

    os.makedirs("data", exist_ok=True)

    # ----------------------------
    # MLB GAME SLATE
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
    # STARTER + TEAM STAT PROXIES (REAL STRUCTURE PLACEHOLDERS)
    # Later upgrade = MLB API starter mapping
    # ----------------------------

    pitcher_stats = {
        "Yankees": {"whip": 1.18, "k9": 9.4, "bb9": 2.6},
        "Red Sox": {"whip": 1.25, "k9": 8.7, "bb9": 3.1},
        "Dodgers": {"whip": 1.10, "k9": 10.2, "bb9": 2.3},
        "Giants": {"whip": 1.20, "k9": 8.9, "bb9": 2.9},
        "Braves": {"whip": 1.15, "k9": 9.1, "bb9": 2.7},
        "Mets": {"whip": 1.22, "k9": 8.6, "bb9": 3.0},
        "Astros": {"whip": 1.12, "k9": 9.8, "bb9": 2.4},
        "Rangers": {"whip": 1.30, "k9": 8.3, "bb9": 3.3},
        "Cubs": {"whip": 1.28, "k9": 8.5, "bb9": 3.2},
        "Cardinals": {"whip": 1.19, "k9": 9.0, "bb9": 2.8},
    }

    offense_stats = {
        "Yankees": {"obp": 0.330, "k_rate": 0.235},
        "Red Sox": {"obp": 0.320, "k_rate": 0.240},
        "Dodgers": {"obp": 0.345, "k_rate": 0.210},
        "Giants": {"obp": 0.315, "k_rate": 0.250},
        "Braves": {"obp": 0.335, "k_rate": 0.225},
        "Mets": {"obp": 0.310, "k_rate": 0.255},
        "Astros": {"obp": 0.325, "k_rate": 0.230},
        "Rangers": {"obp": 0.318, "k_rate": 0.245},
        "Cubs": {"obp": 0.312, "k_rate": 0.252},
        "Cardinals": {"obp": 0.321, "k_rate": 0.238},
    }

    park_factor = {
        "Yankees": 1.03,
        "Red Sox": 1.05,
        "Dodgers": 0.98,
        "Giants": 0.94,
        "Braves": 1.01,
        "Mets": 0.97,
        "Astros": 1.02,
        "Rangers": 1.08,
        "Cubs": 1.00,
        "Cardinals": 0.99,
    }

    # ----------------------------
    # FEATURE ENGINEERING
    # ----------------------------

    def build_features(row):
        away = row["away_team"]
        home = row["home_team"]

        p_away = pitcher_stats[away]
        p_home = pitcher_stats[home]

        o_away = offense_stats[away]
        o_home = offense_stats[home]

        return pd.Series({
            "pitching_whip": p_away["whip"] + p_home["whip"],
            "pitching_k9": p_away["k9"] + p_home["k9"],
            "pitching_bb9": p_away["bb9"] + p_home["bb9"],
            "offense_obp": o_away["obp"] + o_home["obp"],
            "offense_k": o_away["k_rate"] + o_home["k_rate"],
            "park": park_factor[away] + park_factor[home]
        })

    features = df.apply(build_features, axis=1)
    df = pd.concat([df, features], axis=1)

    # ----------------------------
    # NRFI MODEL (B2 MULTI-FACTOR MODEL)
    # ----------------------------

    base = 0.52

    df["model1"] = (
        base
        - (df["pitching_whip"] - 2.35) * 0.28
        + (df["pitching_k9"] - 18) * 0.01
        - (df["offense_obp"] - 0.64) * 0.85
        + (df["offense_k"] - 0.48) * 0.60
        - (df["park"] - 2.00) * 0.12
    )

    df["model2"] = df["model1"] + 0.015
    df["model3"] = df["model1"] - 0.010

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    # ----------------------------
    # OUTPUT
    # ----------------------------

    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    df.to_csv("data/predictions.csv", index=False)

    print("B2 NRFI MODEL COMPLETE - MULTI FACTOR ACTIVE")

if __name__ == "__main__":
    run()