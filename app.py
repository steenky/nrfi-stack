import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="NRFI Model", layout="wide")

st.title("🔥 MLB NRFI Dashboard")

file_path = "data/predictions.csv"

# ---------------- SAFE LOAD ----------------
if os.path.exists(file_path) and os.path.getsize(file_path) > 10:
    try:
        df = pd.read_csv(file_path)
    except Exception:
        st.error("CSV exists but is corrupted. Re-run prediction pipeline.")
        df = pd.DataFrame()
else:
    st.warning("No prediction data yet. Run pipeline to generate games.")
    df = pd.DataFrame()

# ---------------- STOP CRASHING ----------------
if df.empty:
    st.stop()

# ---------------- CONTINUE NORMAL FLOW ----------------
if "avg_nrfi" not in df.columns:
    df["avg_nrfi"] = df[["model1", "model2", "model3"]].mean(axis=1)

df = df.sort_values("avg_nrfi", ascending=False)

st.dataframe(df)

st.subheader("🔥 Best Plays")

best_plays = df[df["avg_nrfi"] > df["avg_nrfi"].quantile(0.70)]

if len(best_plays) > 0:
    st.dataframe(best_plays)
else:
    st.write("No strong NRFI edges today based on model threshold.")
