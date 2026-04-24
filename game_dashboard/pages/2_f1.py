import streamlit as st
from data.bigquery_client import get_bq_client
from google.oauth2 import service_account
import pandas as pd
import plotly.express as px
from data.formula_fire import (
    load_data_calendar,
    load_data_drivers_championship,
    load_data_race_results,
    load_data_team_championship,
    point_evolution_drivers,
    points_evolution_teams
)




##### BACKEND ######
# season = st.selectbox("Select Season", options=[2026], index=0)
season = 2026

calendar_df = load_data_calendar(season)
championship_df = load_data_drivers_championship(season)
race_results_df = load_data_race_results(season)
team_championship_df = load_data_team_championship(season)
points_evolution_drivers_df = point_evolution_drivers(season)
points_evolution_teams_df = points_evolution_teams(season)




round_zero_drivers = pd.DataFrame({
    "Driver": points_evolution_drivers_df["Driver"].unique(),
    "Event": "Start",
    "EventDate": pd.Timestamp("1900-01-01"),  # ← use a real early date instead of Timestamp.min
    "Cumulative_Points": 0
})

points_evolution_drivers_df = (
    pd.concat([round_zero_drivers, points_evolution_drivers_df])
    .assign(EventDate=lambda df: pd.to_datetime(df["EventDate"]))  # ← normalize the column
    .sort_values(["Driver", "EventDate"])
    .reset_index(drop=True)
)


round_zero_teams = pd.DataFrame({
    "Driver": points_evolution_teams_df["Team"].unique(),
    "Event": "Start",
    "EventDate": pd.Timestamp("1900-01-01"),  # ← use a real early date instead of Timestamp.min
    "Cumulative_Points": 0
})

points_evolution_teams_df = (
    pd.concat([round_zero_teams, points_evolution_teams_df])
    .assign(EventDate=lambda df: pd.to_datetime(df["EventDate"]))  # ← normalize the column
    .sort_values(["Team", "EventDate"])
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

points_evolution_drivers_df = points_evolution_drivers_df.sort_values("EventDate")
event_order_drivers = points_evolution_drivers_df["Event"].unique().tolist()

points_evolution_teams_df = points_evolution_teams_df.sort_values("EventDate")
event_order_teams = points_evolution_teams_df["Event"].unique().tolist()



if view == "Drivers":
    fig1 = px.line(
    points_evolution_drivers_df,
    x="Event",
    y="Cumulative_Points",
    color="Driver",
    title="Drivers Championship — Cumulative Points",
    markers=True,
    category_orders={"Event": event_order_drivers},
    labels={
        "Event": "Race",
        "Cumulative_Points": "Points",
    }
    )

    fig1.update_layout(
        xaxis_tickangle=-45,
        legend_title="Driver",
    )

    st.plotly_chart(fig1, use_container_width=True)


else:
    fig2 = px.line(
    points_evolution_teams_df,
    x="Event",
    y="Cumulative_Points",
    color="Team",
    title="Teams Championship — Cumulative Points",
    markers=True,
    category_orders={"Event": event_order_teams},
    labels={
        "Event": "Race",
        "Cumulative_Points": "Points",
    }
    )

    fig2.update_layout(
        xaxis_tickangle=-45,
        legend_title="Team",
    )

    st.plotly_chart(fig2, use_container_width=True)
