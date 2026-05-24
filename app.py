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
# SHOW AVAILABLE COLUMNS
# ----------------------------

st.subheader("Detected Columns")

st.write(list(df.columns))

# ----------------------------
# REQUIRED COLUMNS
# ----------------------------

required_cols = [
    "away_team",
    "home_team",
    "avg_nrfi"
]

missing = [c for c in required_cols if c not in df.columns]

if len(missing) > 0:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# ----------------------------
# OPTIONAL COLUMNS
# ----------------------------

optional_cols = [
    "away_pitcher",
    "home_pitcher",
    "edge_tier"
]

display_cols = required_cols.copy()

for col in optional_cols:
    if col in df.columns:
        display_cols.append(col)

# ----------------------------
# MAIN TABLE
# ----------------------------

st.subheader("All Matchups")

st.dataframe(
    df[display_cols],
    use_container_width=True
)

# ----------------------------
# BEST PLAYS
# ----------------------------

st.subheader("🔥 Best NRFI Plays")

if "edge_tier" in df.columns:

    best = df[df["edge_tier"] != "PASS"]

    if len(best) > 0:
        st.dataframe(
            best[display_cols],
            use_container_width=True
        )
    else:
        st.write("No strong edges today.")

else:

    best = df[df["avg_nrfi"] > df["avg_nrfi"].quantile(0.7)]

    st.dataframe(
        best[display_cols],
        use_container_width=True
    )

# ----------------------------
# TIMESTAMP
# ----------------------------

if "timestamp" in df.columns:
    st.caption(
        f"Last Updated: {df['timestamp'].iloc[0]}"
    )