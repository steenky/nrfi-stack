import pandas as pd

def run():
    # TEMP: sample structure (we replace with real data next step)
    df = pd.DataFrame([
        {
            "away_team": "Yankees",
            "home_team": "Red Sox",
            "model1": 0.62,
            "model2": 0.70,
            "model3": 0.74,
        }
    ])

    df["avg_nrfi"] = df[["model1","model2","model3"]].mean(axis=1)

    df.to_csv("Data/Predictions.csv", index=False)

if __name__ == "__main__":
    run()
