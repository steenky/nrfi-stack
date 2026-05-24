import streamlit as st
import pandas as pd

st.set_page_config(page_title="NRFI Dashboard", layout="wide")

st.title("⚾ NRFI Predictor Dashboard")

file_path = "data/predictions.csv"

try:
    df = pd.read_csv(file_path)
except:
    st.write("No data yet - run pipeline first")
    st.stop()

st.subheader("All Games")

st.dataframe(df, use_container_width=True)

st.subheader("🔥 Best Plays")

best = df[df["avg_nrfi"] > df["avg_nrfi"].quantile(0.7)]

if len(best) > 0:
    st.dataframe(best, use_container_width=True)
else:
    st.write("No strong NRFI edges today")