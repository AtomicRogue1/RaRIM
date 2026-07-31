import streamlit as st
import pandas as pd
from datacollector import DataCollectAndUpdate
from timedecayupdater import update_time_decay
from sentimentupdater import update_sentiment
from impactupdater import update_impact
from database import connect_to_db

companies = (
    "Wayve", "Revolut", "Deliveroo", "Darktrace", "Monzo",
    "Octopus+Energy", "Google", "Signal+AI", "H&M", "Meta"
)

st.title("RaRIM")

selected_company = st.selectbox("Please select the organization.", companies)

conn = connect_to_db()
try:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT collected_at, impact
            FROM articles
            WHERE company = %s
            AND impact IS NOT NULL
            ORDER BY collected_at
        """, (selected_company,))
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

daily = daily.rename(columns={
    "day": "Timeline",
    "impact": "Average Impact"
})

st.line_chart(daily, x="Timeline", y="Average Impact")