import streamlit as st
import pandas as pd
from datacollector import DataCollectAndUpdate
from timedecayupdater import update_time_decay
from sentimentupdater import update_sentiment
from impactupdater import update_impact
from riskheatmap import risk_heatmap
from database import connect_to_db
from datetime import date, timedelta

st.set_page_config(
    page_title="RaRIM",
    layout="wide"
)

companies = (
    "Tesla","Infosys","HSBC+UK"
)

st.title("RaRIM")

controls, emptyspace = st.columns([2,1])

with controls:
    col1, col2 = st.columns(2)
    with col1:
        selected_company = st.selectbox(
            "Please select the organization.",
            companies
        )

    with col2:
        date_range = st.date_input(
            "Select date range",
            value=(
                date.today() - timedelta(days=30),
                date.today()
            )
        )

col3, col4 = st.columns(2)

with col3:
    if(len(date_range) == 2):
        start_date, end_date = date_range
        conn = connect_to_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT collected_at, impact
                    FROM articles
                    WHERE company = %s
                    AND impact IS NOT NULL
                    AND collected_at >= %s
                    AND collected_at < %s + INTERVAL '1 day'
                    ORDER BY collected_at
                """, (selected_company, start_date, end_date))
                rows = cursor.fetchall()
        finally:
            conn.close()

        df = pd.DataFrame(rows, columns=["collected_at", "impact"])

        df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")
        df["impact"] = pd.to_numeric(df["impact"], errors="coerce").astype(float)
        df = df.dropna()

        daily = (
            df.assign(day=df["collected_at"].dt.floor("D"))
            .groupby("day", as_index=False)["impact"]
            .mean()
        )

        daily["Cumulative Impact"] = daily["impact"].cumsum()

        daily = daily.rename(columns={
            "day": "Timeline",
            "Cumulative Impact": "Cumulative Daily Impact"
        })


        st.line_chart(daily, x="Timeline", y="Cumulative Daily Impact")
    else:
        st.caption("Please choose a date range.")

with col4:
    if len(date_range) == 2:
        start_date, end_date = date_range
        conn = connect_to_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT collected_at, risk_category
                    FROM articles
                    WHERE company = %s
                    AND risk_category IS NOT NULL
                    AND collected_at >= %s
                    AND collected_at < %s + INTERVAL '1 day'
                    ORDER BY collected_at
                """, (selected_company, start_date, end_date))
                rows = cursor.fetchall()
        finally:
            conn.close()

        if rows:
            df = pd.DataFrame(rows, columns=["collected_at", "risk_category"])
            df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")
            df = df.dropna()

            daily = (
                df.assign(day=df["collected_at"].dt.floor("D"))
                .groupby(["day", "risk_category"])
                .size()
                .reset_index(name="count")
            )

            categories = [
                "Financial Risks",
                "Product Risks",
                "Legal Risks",
                "Reputational Risks",
                "Governance Risks",
                "Political Unrest",
            ]

            chart_df = pd.DataFrame({
                "Timeline": pd.date_range(start_date, end_date, freq="D")
            })

            for category in categories:
                counts = daily[daily["risk_category"] == category].set_index("day")["count"]
                chart_df[category] = chart_df["Timeline"].map(counts).fillna(0).astype(int)

            st.line_chart(chart_df.set_index("Timeline"), y_label="Risk Frequency")
        else:
            st.caption("No risk data found for this range.")
    else:
        st.caption("Please choose a date range.")

risk_heatmap()