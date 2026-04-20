import streamlit as st
import plotly.express as px
import pandas as pd

from data.bigquery_football import (
    get_available_leagues,
    get_available_seasons,
    get_football_kpis,
    get_team_form_data,
    get_player_stats,
    get_team_season_stats,
    get_home_away_summary,
    get_team_metrics_overview,
    get_team_radar_metrics,
    get_points_distribution_data,
    get_bubble_chart_data,
)
from components.charts import line_chart, bar_chart, scatter_chart

st.markdown(
    """
    <style>
        .block-container {
            max-width: 100% !important;
            padding-left: 3rem;
            padding-right: 3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚽ Football Dashboard")

# Sidebar filters
leagues = get_available_leagues()
league = st.sidebar.selectbox("League", leagues)

seasons = get_available_seasons(league)
season = st.sidebar.selectbox("Season", seasons)

st.caption(f"League: {league} | Season: {season}")

# KPIs
kpis = get_football_kpis(league, season)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Matches", kpis["matches"])
c2.metric("Goals", kpis["goals"])
c3.metric("xG", kpis["xg"])
c4.metric("Wins", kpis["wins"])

# Load datasets
team_stats_df = get_team_season_stats(league)
players_df = get_player_stats(league, season)
home_away_df = get_home_away_summary(league, season)
overview_df = get_team_metrics_overview(league, season)
radar_df = get_team_radar_metrics(league, season)
points_dist_df = get_points_distribution_data(league, season)
bubble_df = get_bubble_chart_data(league, season)

# Team form section
st.divider()
st.subheader("📈 Team Form")

if not team_stats_df.empty:
    available_teams = sorted(team_stats_df["team"].dropna().unique().tolist())
    selected_team = st.selectbox("Choose a team", available_teams, key="selected_team_form")

    form_df = get_team_form_data(league, season, selected_team)

    if not form_df.empty:
        line_chart(
            form_df,
            x="matchday",
            y="points",
            title=f"{selected_team} - Cumulative Points",
        )
    else:
        st.warning("No team form data available.")
else:
    st.warning("No team data available for this league.")

# Player charts
st.divider()
st.subheader("🎯 Player Performance")

col1, col2 = st.columns(2)

with col1:
    if not players_df.empty:
        top_scorers_df = players_df.head(10)
        bar_chart(
            top_scorers_df,
            x="player",
            y="goals",
            title="Top Scorers",
        )
    else:
        st.warning("No player stats available.")

with col2:
    if not players_df.empty:
        scatter_chart(
            players_df.head(30),
            x="assists",
            y="goals",
            size="appearances",
            color="team",
            title="Goals vs Assists",
        )
    else:
        st.warning("No player comparison data available.")

# Team comparison by season
st.divider()
st.subheader("📊 Team Comparison by Season")

if not team_stats_df.empty:
    teams = sorted(team_stats_df["team"].dropna().unique().tolist())

    compare_col1, compare_col2 = st.columns(2)

    with compare_col1:
        team_1 = st.selectbox("Choose first team", teams, key="team_1")

    with compare_col2:
        team_2 = st.selectbox(
            "Choose second team",
            [team for team in teams if team != team_1],
            key="team_2",
        )

    comparison_df = team_stats_df[
        team_stats_df["team"].isin([team_1, team_2])
    ].copy()

    comparison_df["year"] = comparison_df["year"].astype(str)

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
else:
    st.warning("No team season data available.")

# Home vs away section
st.divider()
st.subheader("🏟️ Home vs Away Analysis")

if not home_away_df.empty:
    home_sorted = (
        home_away_df[home_away_df["homeaway"] == "home"]
        .sort_values("win_rate", ascending=False)
    )

    ordered_teams = home_sorted["team_name"].tolist()

    home_away_df["team_name"] = pd.Categorical(
        home_away_df["team_name"],
        categories=ordered_teams,
        ordered=True,
    )

    home_away_df = home_away_df.sort_values("team_name")

    fig_win = px.bar(
        home_away_df,
        x="team_name",
        y="win_rate",
        color="homeaway",
        barmode="group",
        title="Win Rate: Home vs Away",
    )
    fig_win.update_layout(
        xaxis_title="Team",
        yaxis_title="Win Rate",
        legend_title="Venue",
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_win, use_container_width=True)

    fig_goals = px.bar(
        home_away_df,
        x="team_name",
        y="avg_goals",
        color="homeaway",
        barmode="group",
        title="Average Goals: Home vs Away",
    )
    fig_goals.update_layout(
        xaxis_title="Team",
        yaxis_title="Average Goals",
        legend_title="Venue",
        xaxis_tickangle=-45,
    )
    st.plotly_chart(fig_goals, use_container_width=True)
else:
    st.warning("No home vs away data available.")

# New section: heatmap
st.divider()
st.subheader("🔥 Team Metrics Heatmap")

if not overview_df.empty:
    heatmap_df = overview_df.set_index("team_name")[
    ["points", "expected_goals", "Ball_Possession", "Passes_pct", "Total_Shots", "Corner_Kicks"]
]

# Normalize per column
heatmap_norm = (heatmap_df - heatmap_df.min()) / (heatmap_df.max() - heatmap_df.min())

fig_heatmap = px.imshow(
    heatmap_norm,
    text_auto=".2f",
    aspect="auto",
    title="Team Performance Heatmap (Normalized)",
)

fig_heatmap.update_layout(
    xaxis_title="Metric",
    yaxis_title="Team",
)

st.plotly_chart(fig_heatmap, use_container_width=True)
# New section: radar chart
st.divider()
st.subheader("🕸️ Team Radar Comparison")

if not radar_df.empty:
    radar_teams = sorted(radar_df["team_name"].dropna().unique().tolist())

    rcol1, rcol2 = st.columns(2)
    with rcol1:
        radar_team_1 = st.selectbox("Radar Team 1", radar_teams, key="radar_team_1")
    with rcol2:
        radar_team_2 = st.selectbox(
            "Radar Team 2",
            [t for t in radar_teams if t != radar_team_1],
            key="radar_team_2",
        )

    metrics = ["Ball_Possession", "Passes_pct", "Total_Shots", "expected_goals", "Corner_Kicks"]

    radar_filtered = radar_df[radar_df["team_name"].isin([radar_team_1, radar_team_2])].copy()
    radar_long = radar_filtered.melt(
        id_vars="team_name",
        value_vars=metrics,
        var_name="metric",
        value_name="value",
    )

    fig_radar = px.line_polar(
        radar_long,
        r="value",
        theta="metric",
        color="team_name",
        line_close=True,
        title=f"{radar_team_1} vs {radar_team_2} - Team Profile",
    )
    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.warning("No radar chart data available.")

# New section: box plot
st.divider()
st.subheader("📦 Points Distribution")

if not points_dist_df.empty:
    fig_box = px.box(
        points_dist_df,
        x="homeaway",
        y="points",
        color="homeaway",
        title="Points Distribution: Home vs Away",
    )
    fig_box.update_layout(
        xaxis_title="Venue",
        yaxis_title="Points",
        showlegend=False,
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.warning("No points distribution data available.")

# New section: bubble chart
st.divider()
st.subheader("🫧 Team Efficiency Bubble Chart")

if not bubble_df.empty:
    fig_bubble = px.scatter(
        bubble_df,
        x="expected_goals",
        y="points",
        size="Ball_Possession",
        color="team_name",
        hover_name="team_name",
        title="Expected Goals vs Points",
    )
    fig_bubble.update_layout(
        xaxis_title="Average Expected Goals",
        yaxis_title="Total Points",
        legend_title="Team",
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
else:
    st.warning("No bubble chart data available.")

# Player table
st.divider()
st.subheader("🧾 Player Stats")

if not players_df.empty:
    st.dataframe(players_df, use_container_width=True)
else:
    st.warning("No player table available.")
