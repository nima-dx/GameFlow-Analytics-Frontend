import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Connect
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project="le-wagon-data-atelier")

@st.cache_data
def load_data_calendar(season):
    query = f"""
        SELECT
            CASE WHEN strStatus = 'Match Finished' THEN 'Completed' ELSE 'Upcoming' END AS Status,
            strEvent,
            strCountry AS Country,
            CASE WHEN strVenue IS NULL THEN CONCAT(strCity, ' Circuit') ELSE strVenue END AS Circuit,
            FORMAT_DATETIME('%-I%p %B %e, %Y', DATETIME(strTimestamp)) AS DateTime
        FROM `le-wagon-data-atelier.analytics_dataset.f1_calendar`
        WHERE EXTRACT(YEAR FROM dateEvent) = {season}
        ORDER BY dateEvent DESC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()



@st.cache_data
def load_data_race_results(season):
    query = f"""
        SELECT
            intPosition,
            strPlayer as Driver,
            strDetail,
            intPoints,
            strEvent
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results`
        WHERE strSeason = {season}
        LIMIT 1000
    """
    return client.query(query).to_dataframe()



@st.cache_data
def load_data_championship(season):
    query = f"""
        SELECT
            strPlayer,
            SUM(intPoints) AS intPoints
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results`
        WHERE strSeason = {season}
        GROUP BY strPlayer
        ORDER BY intPoints DESC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()




### PAGE LAYOUT STARTS HERE ###

st.title("🏎️ F1 Dashboard")

# --- F1 Header
st.header("Season Calendar 📅")

# --- Season filter ---
season = st.selectbox("Select Season", options=[2024, 2025, 2026], index=2)

calendar_df = load_data_calendar(season)

# Bug 1 fixed: filter on 'Status' (the alias), not 'strStatus'
completed = calendar_df[calendar_df['Status'] == "Completed"]
upcoming = calendar_df[calendar_df['Status'] == "Upcoming"]

# --- F1 Calendar Subheader Completed
# Bug 2 fixed: added f prefix to f-strings
st.subheader(f"Completed Races of {season}")
st.dataframe(completed, hide_index=True)

# --- F1 Calendar Subheader Upcoming
# Bug 3 fixed: corrected label and dataframe to 'upcoming'
st.subheader(f"Upcoming Races of {season}")
st.dataframe(upcoming, hide_index=True)



# --- F1 Header
st.header(f"{season} Championship Results 🏆")

championship_df = load_data_championship(season)
st.dataframe(championship_df, hide_index=True)
