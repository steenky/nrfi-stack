import streamlit as st
import pandas as pd

st.title("⚾ NRFI Predictor (FINAL VERSION)")

df = pd.read_csv("data/predictions.csv")

st.subheader("All Games")
st.dataframe(df, use_container_width=True)

st.subheader("🔥 Best Plays")
st.dataframe(df[df["edge_tier"] != "PASS"], use_container_width=True)

st.caption(df["timestamp"].iloc[0])