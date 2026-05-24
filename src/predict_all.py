import pandas as pd
import os

print("NEW FILE IS RUNNING")

os.makedirs("data", exist_ok=True)

df = pd.DataFrame([
    {
        "away_team": "Yankees",
        "home_team": "Red Sox",
        "away_pitcher": "Cole",
        "home_pitcher": "Bello",
        "edge_tier": "🔥 STRONG NRFI",
        "avg_nrfi": 0.61
    }
])

df.to_csv("data/predictions.csv", index=False)

print(df.columns)
print("CSV WRITTEN")