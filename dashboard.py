import streamlit as st
import pandas as pd

st.set_page_config(page_title="Digital Marketing DSS", layout="wide")
st.title("Digital Marketing DSS")

# --- Session state for action log ---
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []

st.subheader("Live marketing data (simulation)")

EXCEL_FILE = "live_marketing_data.xlsx"

# LOAD DATA
df = pd.read_excel(EXCEL_FILE)

# CLEANING & KPIs
if "campaign_name" in df.columns:
    df = df.dropna(subset=["campaign_name"])

if "c_date" in df.columns:
    df["c_date"] = pd.to_datetime(df["c_date"])

if "status" not in df.columns:
    df["status"] = "ACTIVE"

if "revenue" in df.columns and "mark_spent" in df.columns:
    df["ROAS"] = df["revenue"] / df["mark_spent"]

if "mark_spent" in df.columns and "orders" in df.columns:
    df["CPA"] = df["mark_spent"] / df["orders"]

def recommend_action(roas):
    if pd.isna(roas):
        return "No data"
    if roas < 1:
        return "Pause / Reduce budget"
    elif roas < 2:
        return "Monitor closely"
    else:
        return "Scale up"

if "ROAS" in df.columns:
    df["recommended_action"] = df["ROAS"].apply(recommend_action)

if "c_date" in df.columns and not df.empty:
    df = df.sort_values("c_date")

# ==========================
# 1) ROAS alerts – ONE COLORED TABLE
# ==========================
st.subheader("ROAS alerts")

if "ROAS" in df.columns and not df.empty:
    base_df = df.copy().sort_values("ROAS")

    view_cols = [
        "campaign_name",
        "category",
        "mark_spent",
        "revenue",
        "ROAS",
        "recommended_action",
        "status",
    ]
    view_cols = [c for c in view_cols if c in base_df.columns]
    view_df = base_df[view_cols].copy()

    def roas_color(val):
        if pd.isna(val):
            return ""
        if val < 1:
            return "background-color: #ffcccc"   # red
        elif val < 2:
            return "background-color: #fff3cd"   # yellow
        else:
            return "background-color: #d4edda"   # green

    styled_view = view_df.style.map(roas_color, subset=["ROAS"])

    st.write("Campaigns (one table, ROAS with colors):")
    st.dataframe(styled_view, use_container_width=True, height=420)

    # Simple action controls below the table
    st.write("Select a campaign and apply an action:")

    campaign_list = base_df["campaign_name"].dropna().astype(str).unique()
    selected_campaign = st.selectbox("Campaign:", sorted(campaign_list))

    action = st.selectbox(
        "Action:",
        ["No action", "Pause campaign", "Reduce budget -50%"],
    )

    if st.button("Apply selected action"):
        if action == "Pause campaign":
            df.loc[df["campaign_name"] == selected_campaign, "status"] = "PAUSED_CONFIRMED"
            st.session_state["action_log"].append(
                {"campaign": selected_campaign, "action": "pause_confirmed"}
            )
            st.success(f"Campaign '{selected_campaign}' paused (simulation).")
        elif action == "Reduce budget -50%":
            df.loc[df["campaign_name"] == selected_campaign, "mark_spent"] *= 0.5
            st.session_state["action_log"].append(
                {"campaign": selected_campaign, "action": "reduce_budget_50"}
            )
            st.success(f"Budget for '{selected_campaign}' reduced by 50% (simulation).")

        df.to_excel(EXCEL_FILE, index=False)
else:
    st.write("ROAS column not found or no rows. Make sure revenue and mark_spent exist and data is not empty.")

# ===================
# 2) Campaign drill-down
# ===================
st.subheader("Campaign drill-down")

if "campaign_name" in df.columns and not df.empty:
    campaign_list = df["campaign_name"].dropna().astype(str).unique()
    selected_campaign_dd = st.selectbox(
        "Choose a campaign to inspect:", sorted(campaign_list), key="drilldown"
    )

    camp_df = df[df["campaign_name"] == selected_campaign_dd]

    st.write("Details for:", selected_campaign_dd)
    cols_to_show = ["c_date", "category", "mark_spent", "revenue", "ROAS", "status"]
    cols_to_show = [c for c in cols_to_show if c in camp_df.columns]
    st.dataframe(camp_df[cols_to_show], height=250)

    total_spend = camp_df["mark_spent"].sum()
    total_revenue = camp_df["revenue"].sum()
    avg_roas = camp_df["ROAS"].mean()

    st.metric("Total spend", f"{total_spend:,.0f}")
    st.metric("Total revenue", f"{total_revenue:,.0f}")
    st.metric("Average ROAS", f"{avg_roas:.2f}")

    st.subheader("ROAS trend over time")

    if "c_date" in camp_df.columns and "ROAS" in camp_df.columns:
        trend = camp_df.sort_values("c_date").set_index("c_date")["ROAS"]
        st.line_chart(trend)

# ===================
# 3) Alert detail popup (simulation)
# ===================
st.markdown("---")
st.subheader("Alert detail popup (simulation)")

if "ROAS" in df.columns and "campaign_name" in df.columns and not df.empty:
    camp_df = df[df["campaign_name"] == selected_campaign_dd]
    camp_roas = camp_df["ROAS"].mean()
    if camp_roas < 1:
        with st.container(border=True):
            st.markdown(f"### Alert details: `{selected_campaign_dd}`")
            total_spend = camp_df["mark_spent"].sum()
            total_revenue = camp_df["revenue"].sum()
            st.write(f"Total spend: €{total_spend:,.0f}")
            st.write(f"Total revenue: €{total_revenue:,.0f}")
            st.write(f"ROAS: {camp_roas:.2f} (below target 1.0)")

# ===================
# 4) Action log – simple table
# ===================
st.markdown("---")
st.subheader("Action log (simulation)")

if st.session_state["action_log"]:
    log_df = pd.DataFrame(st.session_state["action_log"])
    st.dataframe(log_df, height=200)
else:
    st.write("No actions taken yet.")
