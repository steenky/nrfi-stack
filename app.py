import streamlit as st
import pandas as pd

st.title("NRFI Predictor")

df = pd.read_csv("data/predictions.csv")

st.subheader("All Games")
st.dataframe(df)

st.subheader("Best Plays")
st.dataframe(df[df["edge_tier"] != "PASS"])