import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("🔥 NRFI Multi-Model Dashboard")

df = pd.read_csv("data/predictions.csv")

st.dataframe(df)

st.subheader("🔥 Best Plays")

st.dataframe(df[df["avg_nrfi"] > 0.68])
