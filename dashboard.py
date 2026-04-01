import streamlit as st
import pandas as pd

st.set_page_config(page_title="Digital Marketing DSS", layout="wide")
st.title("Digital Marketing DSS")

# --- Session state for action log ---
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []

st.subheader("Live marketing data (simulation)")

EXCEL_FILE = "live_marketing_data.xlsx"

# Load data
df = pd.read_excel(EXCEL_FILE)

# Clean basic fields
if "campaign_name" in df.columns:
    df = df.dropna(subset=["campaign_name"])

if "c_date" in df.columns:
    df["c_date"] = pd.to_datetime(df["c_date"])

if "status" not in df.columns:
    df["status"] = "ACTIVE"

# KPIs
if "revenue" in df.columns and "mark_spent" in df.columns:
    df["ROAS"] = df["revenue"] 
