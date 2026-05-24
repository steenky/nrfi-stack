import streamlit as st
import pandas as pd

st.title("NRFI Predictor")

df = pd.read_csv("data/predictions.csv")

st.subheader("All Games")
st.dataframe(df)

st.subheader("Best Plays")

best = df[df["edge_tier"] == "🔥 STRONG NRFI"]
st.dataframe(best)