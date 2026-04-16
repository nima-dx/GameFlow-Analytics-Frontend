import streamlit as st
import plotly.express as px

from data.mock_football import (
    get_football_kpis,
    get_team_form_data,
    get_player_stats,
    get_team_season_stats
)
from data.bigquery_football import seasons_sample
from components.charts import line_chart, bar_chart, scatter_chart

st.title("⚽ Football Dashboard")

league = st.sidebar.selectbox("League", ["Premier League", "La Liga", "Serie A"])
season = st.sidebar.selectbox("Season", ["2025/26", "2024/25", "2023/24"])

st.caption(f"League: {league} | Season: {season}")

kpis = get_football_kpis()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches", kpis["matches"])
c2.metric("Goals", kpis["goals"])
c3.metric("xG", kpis["xg"])
c4.metric("Wins", kpis["wins"])

form_df = get_team_form_data()
players_df = get_player_stats()

col1, col2 = st.columns(2)

with col1:
    line_chart(form_df, x="matchday", y="points", title="Points Progression")

with col2:
    bar_chart(players_df, x="player", y="goals", title="Top Scorers")

scatter_chart(
    players_df,
    x="xg",
    y="goals",
    size="minutes",
    color="player",
    title="xG vs Goals",
)

st.subheader("Player stats")

st.dataframe(players_df, use_container_width=True)

#Comparing teams by season
st.divider()
st.subheader("Team comparison by season")

team_stats_df = get_team_season_stats()
teams = sorted(team_stats_df["team"].unique())

compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    team_1 = st.selectbox("Choose first team", teams, key="team_1")

with compare_col2:
    team_2 = st.selectbox(
        "Choose second team",
        [team for team in teams if team != team_1],
        key="team_2",
    )

comparison_df = team_stats_df[team_stats_df["team"].isin([team_1, team_2])]

fig = px.bar(
    comparison_df.sort_values("year"),
    x="year",
    y="points",
    color="team",
     barmode="group",
    title=f"{team_1} vs {team_2} - Points by Year",
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Points",
    legend_title="Team",
)

st.plotly_chart(fig, use_container_width=True)

#TEST BIG QUERY
st.divider()
st.subheader("🧪 BigQuery connection test")

sample_df = seasons_sample()

st.write("Top 5 rows from BigQuery:")
st.dataframe(sample_df, use_container_width=True)
