import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NRFI Predictor",
    layout="wide"
)

st.title("⚾ Advanced NRFI Model (B3-B)")

# ----------------------------
# LOAD DATA
# ----------------------------

try:
    df = pd.read_csv("data/predictions.csv")
except Exception as e:
    st.error(f"Could not load predictions.csv: {e}")
    st.stop()

# ----------------------------
# SHOW DETECTED COLUMNS
# ----------------------------

st.subheader("Detected Columns")
st.write(list(df.columns))

# ----------------------------
# MAIN TABLE
# ----------------------------

st.subheader("All Matchups")

st.dataframe(
    df,
    use_container_width=True
)

# ----------------------------
# BEST PLAYS
# ----------------------------

st.subheader("🔥 Best NRFI Plays")

if "edge_tier" in df.columns:

    best = df[df["edge_tier"] != "PASS"]

else:

    best = df[
        df["avg_nrfi"] >
        df["avg_nrfi"].quantile(0.7)
    ]

st.dataframe(
    best,
    use_container_width=True
)

# ----------------------------
# TIMESTAMP
# ----------------------------

if "timestamp" in df.columns:
    st.caption(
        f"Last Updated: {df['timestamp'].iloc[0]}"
    )