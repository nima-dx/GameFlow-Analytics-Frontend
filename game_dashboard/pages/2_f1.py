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
            strEvent,
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results`
        WHERE strSeason = {season}
        LIMIT 1000
    """
    return client.query(query).to_dataframe()


#idTeam
@st.cache_data
def load_data_championship(season):
    query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(intPoints) DESC) AS Position,
            dr.Driver,
            dr.Team,
            dr.Country,
            SUM(intPoints) AS Points,
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
        JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
        ON rr.strPlayer = dr.Driver
        WHERE strSeason = {season}
        GROUP BY dr.Driver, dr.Team, dr.Country
        ORDER BY Points DESC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()




##### BACKEND ######
# season = st.selectbox("Select Season", options=[2026], index=0)
season = 2026

calendar_df = load_data_calendar(season)
championship_df = load_data_championship(season)
race_results_df = load_data_race_results(season)




### PAGE LAYOUT STARTS HERE ###
if st.button("Clear cache"):
    st.cache_data.clear()

st.title("🏎️ F1 Dashboard")



st.divider()

# Load Data


# Top KPIs
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Races", calendar_df["strEvent"].nunique())

with k2:
    st.metric("Circuits", calendar_df["strEvent"].nunique())

with k3:
    st.metric("Teams", championship_df["Team"].nunique())

with k4:
    st.metric("Drivers", championship_df["Driver"].nunique())

st.divider()


st.header(f"🏆 {season} Championship Standings 🏆")
st.dataframe(championship_df, hide_index=True)

st.divider()


# --- F1 Header
st.header("📅 Season Calendar 📅")

# --- Season filter ---

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
