import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NRFI Predictor",
    layout="wide"
)

st.title("⚾ Advanced NRFI Model (B3-B)")

try:
    df = pd.read_csv("data/predictions.csv")
except:
    st.error("No predictions found.")
    st.stop()

# ----------------------------
# MAIN TABLE
# ----------------------------

st.subheader("All Matchups")

st.dataframe(
    df[
        [
            "away_team",
            "home_team",
            "away_pitcher",
            "home_pitcher",
            "avg_nrfi",
            "edge_tier"
        ]
    ],
    use_container_width=True
)

# ----------------------------
# BEST PLAYS
# ----------------------------

st.subheader("🔥 Best NRFI Plays")

best = df[df["edge_tier"] != "PASS"]

if len(best) > 0:
    st.dataframe(
        best[
            [
                "away_team",
                "home_team",
                "avg_nrfi",
                "edge_tier"
            ]
        ],
        use_container_width=True
    )
else:
    st.write("No strong edges today.")

# ----------------------------
# TIMESTAMP
# ----------------------------

st.caption(
    f"Last Updated: {df['timestamp'].iloc[0]}"
)