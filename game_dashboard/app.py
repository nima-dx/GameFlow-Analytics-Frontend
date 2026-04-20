import streamlit as st
from pathlib import Path

from data.bigquery_football import (
    get_available_leagues,
    get_available_seasons,
    get_football_kpis,
    get_player_stats,
    get_team_metrics_overview,
)
from data.mock_f1 import get_f1_kpis, get_podiums_data

st.set_page_config(
    page_title="GameFlow Analytics",
    page_icon="📊",
    layout="wide",
)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

TEAM_IMAGE_MAP = {
    "Paris SG": "paris_sg.png",
    "Marseille": "marseille.png",
    "Monaco": "monaco.png",
    "Lyon": "lyon.png",
    "Nice": "nice.png",
    "Lille": "lille.png",
    "Lens": "lens.png",
    "Rennes": "rennes.png",
    "Brest": "brest.png",
    "Toulouse": "toulouse.png",
    "Arsenal": "arsenal.png",
    "Red Bull Racing": "redbull.png",
}

st.markdown(
    """
    <style>
    .block-container {
        max-width: 100% !important;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .kpi-card {
        border-radius: 14px;
        padding: 18px 14px;
        background-color: #f8f9fc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }

    .kpi-icon {
        font-size: 80px;
        margin-bottom: 6px;
        line-height: 1;
    }

    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        line-height: 1.1;
    }

    .kpi-label {
        font-size: 13px;
        color: #666;
        margin-top: 6px;
    }

    div.stButton > button {
        background-color: #f1f3f5;
        color: #333;
        border-radius: 10px;
        padding: 10px 18px;
        border: 1px solid #ddd;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #e0e0e0;
        border-color: #bbb;
        transform: translateY(-1px);
    }

    div.stButton > button:active {
        transform: scale(0.98);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(icon: str, value, label: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_logo_card(name: str, subtitle: str, fallback_emoji: str):
    image_name = TEAM_IMAGE_MAP.get(name, "")
    image_path = ASSETS_DIR / image_name if image_name else None

    with st.container(border=True):
        left, right = st.columns([2, 2], vertical_alignment="center")

        with left:
            if image_path and image_path.exists():
                st.image(str(image_path), width=300)
            else:
                st.markdown(
                    f"<div style='font-size: 2rem; text-align:center;'>{fallback_emoji}</div>",
                    unsafe_allow_html=True,
                )

        with right:
            st.markdown(f"**{name}**")
            st.caption(subtitle)


def show_stat_card(
    title: str,
    main_label: str,
    main_value: str,
    caption_text: str,
    icon_filename: str | None = None,
    fallback_emoji: str = "⭐",
):
    with st.container(border=True):
        st.markdown(f"**{title}**")

        left, right = st.columns([2.5, 2], vertical_alignment="top")

        with left:
            st.markdown(f"**{main_label}**")
            st.markdown(
                f"<div style='font-size: 1.2rem; font-weight: 700; margin: 0.2rem 0 0.3rem 0;'>{main_value}</div>",
                unsafe_allow_html=True,
            )
            st.caption(caption_text)

        with right:
            icon_path = ICONS_DIR / icon_filename if icon_filename else None
            if icon_path and icon_path.exists():
                st.image(str(icon_path), width=100)
            else:
                st.markdown(
                    f"<div style='font-size: 2rem; text-align:center;'>{fallback_emoji}</div>",
                    unsafe_allow_html=True,
                )


football_leagues = get_available_leagues()
default_league = football_leagues[0] if football_leagues else None

default_season = None
football_kpis = {"matches": 0, "goals": 0, "xg": 0, "wins": 0}
players_df = None
overview_df = None
featured_team = "Football Team"
top_scorer = None

if default_league:
    seasons = get_available_seasons(default_league)
    default_season = seasons[0] if seasons else None

    if default_season:
        football_kpis = get_football_kpis(default_league, default_season)
        players_df = get_player_stats(default_league, default_season)
        overview_df = get_team_metrics_overview(default_league, default_season)

        if overview_df is not None and not overview_df.empty:
            featured_team = (
                overview_df.sort_values("points", ascending=False).iloc[0]["team_name"]
            )

        if players_df is not None and not players_df.empty:
            top_scorer = players_df.sort_values("goals", ascending=False).iloc[0]

f1_kpis = get_f1_kpis()
podiums_df = get_podiums_data()
top_driver = podiums_df.sort_values("podiums", ascending=False).iloc[0]

st.markdown(
    """
    <h1 style="
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #ff8c00, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    ">
    GameFlow Analytics
    </h1>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Welcome to the dashboard")
st.write("Explore football and Formula 1 analytics from the sidebar.")

if default_league and default_season:
    st.caption(f"Football snapshot: {default_league} | {default_season}")

st.divider()

st.subheader("Overview")
k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("⚽", football_kpis["matches"], "Football Matches")

with k2:
    kpi_card("🥅", football_kpis["goals"], "Football Goals")

with k3:
    kpi_card("🏎️", f1_kpis["races"], "F1 Races")

with k4:
    kpi_card("🏆", f1_kpis["podiums"], "F1 Podiums")

st.divider()

st.subheader("Featured")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Football")
    left_card, right_card = st.columns(2)

    with left_card:
        show_logo_card(
            name=featured_team,
            subtitle=f"Top team in {default_league}" if default_league else "Featured club",
            fallback_emoji="⚽",
        )

    with right_card:
        if top_scorer is not None:
            show_stat_card(
                title="Top scorer",
                main_label=top_scorer["player"],
                main_value=f"{int(top_scorer['goals'])} goals",
                caption_text=f"Team: {top_scorer['team']} | Assists: {int(top_scorer['assists'])}",
                icon_filename="ppp.png",
                fallback_emoji="⚽",
            )
        else:
            show_stat_card(
                title="Top scorer",
                main_label="No scorer data",
                main_value="—",
                caption_text="No scorer data available.",
                icon_filename="player.png",
                fallback_emoji="⚽",
            )

    if st.button("👉 Go to Football", key="go_football"):
        st.switch_page("pages/1_football.py")

with c2:
    st.markdown("#### Formula 1")
    left_card, right_card = st.columns(2)

    with left_card:
        show_logo_card(
            name="Red Bull Racing",
            subtitle="Featured team",
            fallback_emoji="🏎️",
        )

    with right_card:
        show_stat_card(
            title="Top driver",
            main_label=top_driver["driver"],
            main_value=f"{top_driver['podiums']} podiums",
            caption_text="Best podium total in mock dataset",
            icon_filename="helmet.png",
            fallback_emoji="🏎️",
        )

    if st.button("👉 Go to F1", key="go_f1"):
        st.switch_page("pages/2_f1.py")

st.divider()

st.subheader("Quick Access")
q1, q2 = st.columns(2)

with q1:
    with st.container(border=True):
        st.markdown("**Football insights**")
        if default_league and default_season:
            st.write(f"Real data from {default_league} ({default_season})")
        else:
            st.write("Football data unavailable")

with q2:
    with st.container(border=True):
        st.markdown("**F1 insights**")
        st.write("Driver standings, podiums, qualifying vs finish")

st.info("Football now uses BigQuery data. Formula 1 is still using mock data.")
