import streamlit as st
import pandas as pd

st.title("NRFI Debug View")

df = pd.read_csv("data/predictions.csv")

st.subheader("RAW COLUMNS")
st.write(df.columns.tolist())

st.subheader("RAW DATA")
st.dataframe(df)

if "edge_tier" in df.columns:
    st.subheader("Best Plays")
    st.dataframe(df[df["edge_tier"] != "PASS"])
else:
    st.error("edge_tier column is missing — model did NOT generate correctly")