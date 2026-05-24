import pandas as pd
import numpy as np
import os
from datetime import datetime

print(">>> V2 MODEL EXECUTING <<<")

def run():

    # ----------------------------
    # CREATE OUTPUT FOLDER SAFELY
    # ----------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)

    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    output_path = os.path.join(data_dir, "predictions.csv")

    print("WRITING TO:", output_path)

    # ----------------------------
    # SAMPLE MLB SLATE (STATIC FOR NOW)
    # ----------------------------
    games = [
        {"away_team": "Yankees", "home_team": "Red Sox", "away_pitcher": "Cole", "home_pitcher": "Bello"},
        {"away_team": "Dodgers", "home_team": "Giants", "away_pitcher": "Yamamoto", "home_pitcher": "Webb"},
        {"away_team": "Braves", "home_team": "Mets", "away_pitcher": "Strider", "home_pitcher": "Senga"},
        {"away_team": "Astros", "home_team": "Rangers", "away_pitcher": "Valdez", "home_pitcher": "Eovaldi"},
        {"away_team": "Cubs", "home_team": "Cardinals", "away_pitcher": "Steele", "home_pitcher": "Gray"},
    ]

    df = pd.DataFrame(games)

    # ----------------------------
    # PITCHER METRICS
    # ----------------------------
    pitchers = {
        "Cole": {"whip": 1.05, "k9": 10.8, "bb9": 2.1, "hr9": 0.8},
        "Bello": {"whip": 1.31, "k9": 8.2, "bb9": 3.3, "hr9": 1.1},
        "Yamamoto": {"whip": 1.02, "k9": 10.4, "bb9": 2.0, "hr9": 0.7},
        "Webb": {"whip": 1.15, "k9": 8.5, "bb9": 1.9, "hr9": 0.9},
        "Strider": {"whip": 1.09, "k9": 13.2, "bb9": 2.8, "hr9": 0.9},
        "Senga": {"whip": 1.20, "k9": 10.1, "bb9": 3.4, "hr9": 0.8},
        "Valdez": {"whip": 1.14, "k9": 9.1, "bb9": 2.9, "hr9": 0.7},
        "Eovaldi": {"whip": 1.18, "k9": 8.9, "bb9": 2.2, "hr9": 1.0},
        "Steele": {"whip": 1.16, "k9": 9.4, "bb9": 2.5, "hr9": 0.8},
        "Gray": {"whip": 1.21, "k9": 9.0, "bb9": 2.7, "hr9": 0.9},
    }

    # ----------------------------
    # OFFENSE METRICS
    # ----------------------------
    offense = {
        "Yankees": {"obp": 0.334, "k_rate": 0.238},
        "Red Sox": {"obp": 0.321, "k_rate": 0.241},
        "Dodgers": {"obp": 0.346, "k_rate": 0.212},
        "Giants": {"obp": 0.314, "k_rate": 0.249},
        "Braves": {"obp": 0.337, "k_rate": 0.227},
        "Mets": {"obp": 0.312, "k_rate": 0.253},
        "Astros": {"obp": 0.326, "k_rate": 0.231},
        "Rangers": {"obp": 0.319, "k_rate": 0.246},
        "Cubs": {"obp": 0.313, "k_rate": 0.251},
        "Cardinals": {"obp": 0.322, "k_rate": 0.239},
    }

    # ----------------------------
    # PARK FACTORS
    # ----------------------------
    park = {
        "Red Sox": 1.05,
        "Giants": 0.94,
        "Mets": 0.97,
        "Rangers": 1.08,
        "Cardinals": 0.99,
    }

    # ----------------------------
    # FEATURE ENGINEERING
    # ----------------------------
    def build(row):

        ap = pitchers[row["away_pitcher"]]
        hp = pitchers[row["home_pitcher"]]

        ao = offense[row["away_team"]]
        ho = offense[row["home_team"]]

        pf = park.get(row["home_team"], 1.0)

        return pd.Series({
            "whip": ap["whip"] + hp["whip"],
            "k9": ap["k9"] + hp["k9"],
            "bb9": ap["bb9"] + hp["bb9"],
            "hr9": ap["hr9"] + hp["hr9"],
            "obp": ao["obp"] + ho["obp"],
            "k_rate": ao["k_rate"] + ho["k_rate"],
            "park_factor": pf
        })

    features = df.apply(build, axis=1)
    df = pd.concat([df, features], axis=1)

    # ----------------------------
    # MODEL
    # ----------------------------
    base = 0.52

    df["model1"] = (
        base
        - (df["whip"] - 2.3) * 0.25
        + (df["k9"] - 18) * 0.01
        - (df["bb9"] - 5) * 0.02
        - (df["hr9"] - 1.8) * 0.04
        - (df["obp"] - 0.64) * 0.9
        + (df["k_rate"] - 0.48) * 0.6
        - (df["park_factor"] - 1.0) * 0.1
    )

    df["model2"] = df["model1"] + 0.01
    df["model3"] = df["model1"] - 0.01

    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

    # ----------------------------
    # EDGE LOGIC
    # ----------------------------
    df["edge_tier"] = np.where(
        df["avg_nrfi"] >= 0.58,
        "🔥 STRONG NRFI",
        np.where(df["avg_nrfi"] >= 0.54, "✅ LEAN NRFI", "PASS")
    )

    # ----------------------------
    # TIMESTAMP
    # ----------------------------
    df["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ----------------------------
    # SAVE
    # ----------------------------
    df.to_csv(output_path, index=False)

    print("COLUMNS WRITTEN:", df.columns.tolist())
    print("SUCCESS")

if __name__ == "__main__":
    run()