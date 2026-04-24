import streamlit as st
from data.bigquery_client import get_bq_client
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px


# Connect
# credentials = service_account.Credentials.from_service_account_info(
#     st.secrets["gcp_service_account"]
# )
# client = bigquery.Client(credentials=credentials, project="le-wagon-data-atelier")

client = get_bq_client()


@st.cache_data
def load_data_calendar(season):
    query = f"""
        SELECT
            CASE WHEN strStatus = 'Match Finished' THEN 'Completed' ELSE 'Upcoming' END AS Status,
            strEvent AS Event,
            strCountry AS Country,
            CASE
                WHEN strEvent = 'Las Vegas Grand Prix' THEN 'Las Vegas Strip Circuit'
                WHEN strEvent = 'São Paulo Grand Prix' THEN 'Interlagos Circuit'
                ELSE strVenue
            END AS Circuit,
            FORMAT_DATETIME('%-I%p %B %e', DATETIME(strTimestamp)) AS Date
        FROM `le-wagon-data-atelier.analytics_dataset.f1_calendar`
        WHERE EXTRACT(YEAR FROM dateEvent) = {season}
        ORDER BY dateEvent ASC
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
def load_data_drivers_championship(season):
    query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(intPoints) DESC) AS Position,
            dr.Driver AS Driver,
            dr.Team,
            dr.Country,
            SUM(intPoints) AS Points
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
        JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
        ON rr.strPlayer = dr.Driver
        WHERE strSeason = {season}
        GROUP BY dr.Driver, dr.Team, dr.Country
        ORDER BY Position ASC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()

def load_data_team_championship(season):
    query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(intPoints) DESC) AS Position,
            dr.Team,
            SUM(intPoints) AS Points
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
        JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
        ON rr.strPlayer = dr.Driver
        WHERE strSeason = {season}
        GROUP BY dr.Team
        ORDER BY Position ASC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()


def point_evolution_drivers(season):

    query = f"""
        WITH race_data AS (
            SELECT
                strEvent AS Event,
                strPlayer AS Driver,
                dr.Team AS Team,
                intPoints AS Points,
                dateEvent AS EventDate
            FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
            JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
                ON rr.strPlayer = dr.Driver
            WHERE strSeason = {season}
        )

        SELECT
            Event,
            EventDate,
            Driver,
            SUM(Points) AS Points_This_Race,
            SUM(SUM(Points)) OVER (
                PARTITION BY Driver
                ORDER BY EventDate
            ) AS Cumulative_Points
        FROM race_data
        GROUP BY Driver, Event, EventDate
        ORDER BY EventDate ASC, Cumulative_Points DESC
    """
    return client.query(query).to_dataframe()

def points_evolution_teams(season):
    query = f"""
        WITH race_data AS (
            SELECT
                strEvent AS Event,
                dr.Team AS Team,
                intPoints AS Points,
                dateEvent AS EventDate
            FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
            JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
                ON rr.strPlayer = dr.Driver
            WHERE strSeason = {season}
        )

        SELECT
            Event,
            EventDate,
            Team,                              -- ← added missing comma
            SUM(Points) AS Points_This_Race,
            SUM(SUM(Points)) OVER (
                PARTITION BY Team              -- ← was Driver, should be Team
                ORDER BY EventDate
            ) AS Cumulative_Points
        FROM race_data
        GROUP BY Team, Event, EventDate
        ORDER BY EventDate ASC, Cumulative_Points DESC
    """
    return client.query(query).to_dataframe()

##### BACKEND ######
# season = st.selectbox("Select Season", options=[2026], index=0)
season = 2026

calendar_df = load_data_calendar(season)
championship_df = load_data_drivers_championship(season)
race_results_df = load_data_race_results(season)
team_championship_df = load_data_team_championship(season)
points_evolution_drivers_df = point_evolution_drivers(season)
points_evolution_teams_df = points_evolution_teams(season)




round_zero = pd.DataFrame({
    "Driver": points_evolution_teams_df["Team"].unique(),
    "Event": "Start",
    "EventDate": pd.Timestamp("1900-01-01"),  # ← use a real early date instead of Timestamp.min
    "Cumulative_Points": 0
})

points_evolution_drivers_df = (
    pd.concat([round_zero, points_evolution_teams_df])
    .assign(EventDate=lambda df: pd.to_datetime(df["EventDate"]))  # ← normalize the column
    .sort_values(["Driver", "EventDate"])
    .reset_index(drop=True)
)


### PAGE LAYOUT STARTS HERE ###
if st.button("Clear cache"):
    st.cache_data.clear()

st.title("🏎️ F1 Dashboard")



st.divider()

# Load Data


# Top KPIs
k1, k5, k2, k3, k4,  = st.columns(5)

with k1:
    st.metric("Races", calendar_df["Event"].nunique())

with k5:
    st.metric("Races Completed", calendar_df[calendar_df["Status"] == "Completed"]["Event"].nunique())

with k2:
    st.metric("Circuits", calendar_df["Event"].nunique())

with k3:
    st.metric("Teams", championship_df["Team"].nunique())

with k4:
    st.metric("Drivers", championship_df["Driver"].nunique())

st.divider()


view = st.radio("Championship", ["Drivers", "Constructors"], horizontal=True)

if view == "Drivers":
    st.header(f"🏆 {season} Championship Standings 🏆")
    st.dataframe(championship_df, hide_index=True)
else:
    st.header(f"🏆 {season} Constructor Championship Standings 🏆")
    st.dataframe(team_championship_df, hide_index=True,)


st.divider()


# --- F1 Header
st.header("📅 2026 Season Calendar 📅")

# --- Season filter ---

completed = calendar_df[calendar_df['Status'] == "Completed"]
upcoming = calendar_df[calendar_df['Status'] == "Upcoming"]
completed = completed[['Event', 'Circuit', 'Date']]
upcoming = upcoming[['Event', 'Circuit', 'Date']]


# --- F1 Calendar Subheader Completed
# Bug 2 fixed: added f prefix to f-strings
st.write(f"Completed Races of {season}")
st.dataframe(completed, hide_index=True,)


# --- F1 Calendar Subheader Upcoming
# Bug 3 fixed: corrected label and dataframe to 'upcoming'
st.write(f"Upcoming Races of {season}")
st.dataframe(upcoming, hide_index=True)


st.divider()

# Sort by date so events are in the right order
points_evolution_drivers_df = points_evolution_drivers_df.sort_values("EventDate")

# Lock the x-axis order to match chronological order
event_order = points_evolution_drivers_df["Event"].unique().tolist()

fig = px.line(
    points_evolution_drivers_df,
    x="Event",
    y="Cumulative_Points",
    color="Team",
    title="Teams Championship — Cumulative Points",
    markers=True,
    category_orders={"Event": event_order},  # ← forces chronological order
    labels={
        "Event": "Race",
        "Cumulative_Points": "Points",
    }
)

fig.update_layout(
    xaxis_tickangle=-45,
    legend_title="Team",
)

st.plotly_chart(fig, use_container_width=True)
