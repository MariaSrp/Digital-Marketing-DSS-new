import streamlit as st
import pandas as pd

st.set_page_config(page_title="Digital Marketing DSS", layout="wide")
st.title("Digital Marketing DSS")

# --- Session state for action log ---
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []

st.subheader("Live marketing data (simulation)")

EXCEL_FILE = "live_marketing_data.xlsx"

df = pd.read_excel(EXCEL_FILE)

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

# 1) ROAS alerts
st.subheader("ROAS alerts")

if "ROAS" in df.columns:
    base_df = df.copy().sort_values("ROAS")

    if base_df.empty:
        st.write("No rows yet (waiting for data in live_marketing_data.xlsx).")
    else:
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

        view_df["Pause"] = False
        view_df["Reduce_50"] = False

        st.write("Campaigns (scroll inside the table):")

        edited_df = st.data_editor(
            view_df,
            height=400,
            column_config={
                "ROAS": st.column_config.NumberColumn("ROAS", format="%.3f"),
                "Pause": st.column_config.CheckboxColumn("Pause"),
                "Reduce_50": st.column_config.CheckboxColumn("-50%"),
            },
            disabled=[
                "campaign_name",
                "category",
                "mark_spent",
                "revenue",
                "ROAS",
                "recommended_action",
                "status",
            ],
            use_container_width=True,
        )

        st.write("Apply actions for the selected rows:")

        if st.button("Apply actions"):
            for _, row in edited_df.iterrows():
                name = row["campaign_name"]

                if row.get("Pause", False):
                    df.loc[df["campaign_name"] == name, "status"] = "PAUSE_REQUESTED"
                    st.session_state["action_log"].append(
                        {"campaign": name, "action": "pause_requested"}
                    )
                    df.loc[df["campaign_name"] == name, "status"] = "PAUSED_CONFIRMED"
                    st.session_state["action_log"].append(
                        {"campaign": name, "action": "pause_confirmed"}
                    )

                if row.get("Reduce_50", False):
                    df.loc[df["campaign_name"] == name, "mark_spent"] *= 0.5
                    st.session_state["action_log"].append(
                        {"campaign": name, "action": "reduce_budget_50"}
                    )

            df.to_excel(EXCEL_FILE, index=False)
            st.success("Actions applied (simulation).")
else:
    st.write("ROAS column not found. Make sure revenue and mark_spent exist.")

# 2) Campaign drill-down
st.subheader("Campaign drill-down")

if "campaign_name" in df.columns and not df.empty:
    campaign_list = df["campaign_name"].dropna().astype(str).unique()
    selected_campaign = st.selectbox(
        "Choose a campaign to inspect:", sorted(campaign_list)
    )

    camp_df = df[df["campaign_name"] == selected_campaign]

    st.write("Details for:", selected_campaign)
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

# 3) Alert detail popup (simulation)
st.markdown("---")
st.subheader("Alert detail popup (simulation)")

if "ROAS" in df.columns and "campaign_name" in df.columns and not df.empty:
    if "selected_campaign" in locals():
        camp_df = df[df["campaign_name"] == selected_campaign]
        camp_roas = camp_df["ROAS"].mean()
        if camp_roas < 1:
            with st.container(border=True):
                st.markdown(f"### Alert details: `{selected_campaign}`")
                total_spend = camp_df["mark_spent"].sum()
                total_revenue = camp_df["revenue"].sum()
                st.write(f"Total spend: €{total_spend:,.0f}")
                st.write(f"Total revenue: €{total_revenue:,.0f}")
                st.write(f"ROAS: {camp_roas:.2f} (below target 1.0)")

# 4) Action log
st.markdown("---")
st.subheader("Action log (simulation)")

if st.session_state["action_log"]:
    log_df = pd.DataFrame(st.session_state["action_log"])
    st.dataframe(log_df, height=200)
else:
    st.write("No actions taken yet.")
