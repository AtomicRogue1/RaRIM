import streamlit as st
import pandas as pd
from database import connect_to_db
import plotly.express as px
from datetime import date, timedelta

def risk_heatmap():
    st.subheader("Company Risk Heatmap")

    date_range = st.date_input(
        "Heatmap date range",
        value=(
            date.today() - timedelta(days=30),
            date.today()
        ),
        key="heatmap_date_range"
    )

    if len(date_range) != 2:
        st.caption("Please choose a valid date range.")
        return

    start_date, end_date = date_range

    # -----------------------------
    # Get data from PostgreSQL
    # -----------------------------

    conn = connect_to_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    company,
                    risk_category,
                    impact
                FROM articles
                WHERE risk_category IS NOT NULL
                  AND impact IS NOT NULL
                  AND collected_at >= %s
                  AND collected_at < %s + INTERVAL '1 day'
                """,
                (start_date, end_date)
            )

            rows = cursor.fetchall()

    finally:
        conn.close()

    # -----------------------------
    # No data
    # -----------------------------

    if not rows:
        st.caption("No risk data found for this date range.")
        return

    # -----------------------------
    # Create DataFrame
    # -----------------------------

    df = pd.DataFrame(
        rows,
        columns=[
            "company",
            "risk_category",
            "impact"
        ]
    )

    df["impact"] = pd.to_numeric(
        df["impact"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "company",
            "risk_category",
            "impact"
        ]
    )

    # -----------------------------
    # Create heatmap matrix
    # -----------------------------

    heatmap_data = df.pivot_table(
        index="risk_category",
        columns="company",
        values="impact",
        aggfunc="mean"
    )

    # Optional ordering
    risk_order = [
        "Financial Risks",
        "Product Risks",
        "Legal Risks",
        "Reputational Risks",
        "Governance Risks",
        "Political Unrest"
    ]

    # Only keep categories that actually exist
    existing_categories = [
        category
        for category in risk_order
        if category in heatmap_data.index
    ]

    other_categories = [
        category
        for category in heatmap_data.index
        if category not in existing_categories
    ]

    heatmap_data = heatmap_data.reindex(
        existing_categories + other_categories
    )

    # -----------------------------
    # Create Plotly heatmap
    # -----------------------------

    fig = px.imshow(
        heatmap_data,
        text_auto=".2f",
        aspect="auto",
        color_continuous_midpoint=0,
        labels={
            "x": "Company",
            "y": "Risk Category",
            "color": "Average Impact"
        }
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        )
    )

    # -----------------------------
    # Display
    # -----------------------------

    st.plotly_chart(
        fig,
        width="stretch"
    )