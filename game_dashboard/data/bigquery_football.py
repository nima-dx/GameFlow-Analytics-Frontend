from data.bigquery_client import get_bq_client
import pandas as pd
import streamlit as st

PROJECT_ID = "le-wagon-data-atelier"
DATASET_ID = "analytics_dataset"
TABLE_PLAYERS = "players_performance"
TABLE_PERFORMANCE = "team_performance_metrics"


@st.cache_data(ttl=600)
def load_players_performance() -> pd.DataFrame:
    client = get_bq_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_PLAYERS}`
    """

    return client.query(query).to_dataframe()


@st.cache_data(ttl=600)
def load_team_performance() -> pd.DataFrame:
    client = get_bq_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_PERFORMANCE}`
    """

    return client.query(query).to_dataframe()


@st.cache_data(ttl=600)
def get_available_leagues() -> list[str]:
    df = load_team_performance()
    return sorted(df["league_name"].dropna().unique().tolist())


@st.cache_data(ttl=600)
def get_available_seasons(league: str) -> list[str]:
    df = load_team_performance()
    filtered = df[df["league_name"] == league]
    return sorted(filtered["season"].dropna().unique().tolist(), reverse=True)


@st.cache_data(ttl=600)
def get_football_kpis(league: str, season: str) -> dict:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    matches = filtered["event_id"].nunique()
    goals = int(filtered["score"].sum()) if not filtered.empty else 0
    xg = round(filtered["expected_goals"].sum(), 2) if not filtered.empty else 0.0
    wins = int((filtered["points"] == 3).sum()) if not filtered.empty else 0

    return {
        "matches": matches,
        "goals": goals,
        "xg": xg,
        "wins": wins,
    }


@st.cache_data(ttl=600)
def get_team_form_data(league: str, season: str, team: str | None = None) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "matchday",
                "points",
                "team",
                "result",
                "score",
                "expected_goals",
                "rolling_points_5",
            ]
        )

    if team is None:
        best_team = (
            filtered.groupby("team_name", as_index=False)["points"]
            .sum()
            .sort_values("points", ascending=False)
            .iloc[0]["team_name"]
        )
        team = best_team

    team_df = (
        filtered[filtered["team_name"] == team]
        .sort_values(["event_id"])
        .reset_index(drop=True)
        .copy()
    )

    if team_df.empty:
        return pd.DataFrame(
            columns=[
                "matchday",
                "points",
                "team",
                "result",
                "score",
                "expected_goals",
                "rolling_points_5",
            ]
        )

    team_df["matchday"] = range(1, len(team_df) + 1)

    team_df["result"] = team_df["points"].map({
        3: "W",
        1: "D",
        0: "L",
    }).fillna("N/A")

    team_df["rolling_points_5"] = (
        team_df["points"]
        .rolling(window=5, min_periods=1)
        .mean()
        .round(2)
    )

    return team_df[
        [
            "matchday",
            "points",
            "team_name",
            "result",
            "score",
            "expected_goals",
            "rolling_points_5",
        ]
    ].rename(columns={"team_name": "team"})


@st.cache_data(ttl=600)
def get_player_stats(league: str, season: str) -> pd.DataFrame:
    df = load_players_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "player",
                "team",
                "goals",
                "assists",
                "appearances",
                "yellow_cards",
                "red_cards",
            ]
        )

    filtered["goal_contribution"] = (
        filtered["normal_goals"].fillna(0) + filtered["penalties"].fillna(0)
    )

    filtered["assist_flag"] = (
        filtered["assist_name"]
        .fillna("")
        .str.strip()
        .ne("")
        .astype(int)
    )

    grouped = (
        filtered.groupby(["player_name", "team_name"], as_index=False)
        .agg(
            goals=("goal_contribution", "sum"),
            assists=("assist_flag", "sum"),
            appearances=("event_id", "nunique"),
            yellow_cards=("yellow_cards", "sum"),
            red_cards=("red_cards", "sum"),
        )
        .rename(columns={
            "player_name": "player",
            "team_name": "team",
        })
        .sort_values(["goals", "assists"], ascending=[False, False])
    )

    return grouped


@st.cache_data(ttl=600)
def get_team_season_stats(league: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[df["league_name"] == league].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["team", "year", "points"])

    grouped = (
        filtered.groupby(["team_name", "season"], as_index=False)["points"]
        .sum()
        .rename(columns={"team_name": "team"})
    )

    grouped["year"] = grouped["season"].astype(str).str[:4].astype(int)

    return grouped[["team", "year", "points"]].sort_values(["year", "team"])


@st.cache_data(ttl=600)
def get_home_away_summary(league: str, season: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=["team_name", "homeaway", "games", "wins", "win_rate", "avg_goals"]
        )

    filtered["win"] = (filtered["points"] == 3).astype(int)

    summary = (
        filtered.groupby(["team_name", "homeaway"], as_index=False)
        .agg(
            games=("event_id", "nunique"),
            wins=("win", "sum"),
            avg_goals=("score", "mean"),
        )
    )

    summary["win_rate"] = (summary["wins"] / summary["games"]).round(3)

    return summary.sort_values(["team_name", "homeaway"])


@st.cache_data(ttl=600)
def get_team_metrics_overview(league: str, season: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "team_name",
                "points",
                "expected_goals",
                "Ball_Possession",
                "Passes_pct",
                "Total_Shots",
                "Corner_Kicks",
                "score",
            ]
        )

    grouped = (
        filtered.groupby("team_name", as_index=False)
        .agg(
            points=("points", "sum"),
            expected_goals=("expected_goals", "mean"),
            Ball_Possession=("Ball_Possession", "mean"),
            Passes_pct=("Passes_pct", "mean"),
            Total_Shots=("Total_Shots", "mean"),
            Corner_Kicks=("Corner_Kicks", "mean"),
            score=("score", "mean"),
        )
    )

    return grouped


@st.cache_data(ttl=600)
def get_team_radar_metrics(league: str, season: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "team_name",
                "Ball_Possession",
                "Passes_pct",
                "Total_Shots",
                "expected_goals",
                "Corner_Kicks",
            ]
        )

    grouped = (
        filtered.groupby("team_name", as_index=False)
        .agg(
            Ball_Possession=("Ball_Possession", "mean"),
            Passes_pct=("Passes_pct", "mean"),
            Total_Shots=("Total_Shots", "mean"),
            expected_goals=("expected_goals", "mean"),
            Corner_Kicks=("Corner_Kicks", "mean"),
        )
    )

    return grouped


@st.cache_data(ttl=600)
def get_points_distribution_data(league: str, season: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(columns=["team_name", "homeaway", "points"])

    return filtered[["team_name", "homeaway", "points"]]


@st.cache_data(ttl=600)
def get_bubble_chart_data(league: str, season: str) -> pd.DataFrame:
    df = load_team_performance()
    filtered = df[
        (df["league_name"] == league) &
        (df["season"] == season)
    ].copy()

    if filtered.empty:
        return pd.DataFrame(
            columns=[
                "team_name",
                "expected_goals",
                "points",
                "Ball_Possession",
                "Total_Shots",
            ]
        )

    grouped = (
        filtered.groupby("team_name", as_index=False)
        .agg(
            expected_goals=("expected_goals", "mean"),
            points=("points", "sum"),
            Ball_Possession=("Ball_Possession", "mean"),
            Total_Shots=("Total_Shots", "mean"),
        )
    )

    return grouped
