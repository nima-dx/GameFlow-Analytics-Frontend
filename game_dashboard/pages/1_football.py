import streamlit as st

from data.mock_football import (
    get_football_kpis,
    get_team_form_data,
    get_player_stats,
)
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
