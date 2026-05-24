import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="NRFI Model", layout="wide")

st.title("🔥 MLB NRFI Dashboard")

file_path = "data/predictions.csv"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    st.warning("No data yet — run prediction pipeline")
    df = pd.DataFrame()

if len(df) > 0:
    df = df.sort_values("avg_nrfi", ascending=False)

    st.dataframe(df)

    st.subheader("🔥 Best Plays")
    st.dataframe(df[df["avg_nrfi"] > 0.68])