import streamlit as st
from pathlib import Path

from data.mock_football import get_football_kpis, get_player_stats
from data.mock_f1 import get_f1_kpis, get_podiums_data

st.set_page_config(
    page_title="GameFlow Analytics",
    page_icon="📊",
    layout="wide",
)

ASSETS_DIR = Path(__file__).parent / "assets"


def show_logo_card(name: str, subtitle: str, image_name: str, fallback_emoji: str):
    image_path = ASSETS_DIR / image_name

    with st.container(border=True):
        if image_path.exists():
            st.image(str(image_path), width=90)
        else:
            st.markdown(f"<div style='font-size: 3rem'>{fallback_emoji}</div>", unsafe_allow_html=True)

        st.markdown(f"**{name}**")
        st.caption(subtitle)


football_kpis = get_football_kpis()
f1_kpis = get_f1_kpis()

players_df = get_player_stats()
top_scorer = players_df.sort_values("goals", ascending=False).iloc[0]

podiums_df = get_podiums_data()
top_driver = podiums_df.sort_values("podiums", ascending=False).iloc[0]

st.title("⚽🏎️ GameFlow Analytics")
st.markdown("### Welcome to the dashboard")
st.write("Explore football and Formula 1 analytics from the sidebar.")

st.divider()

st.subheader("Overview")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Football Matches", football_kpis["matches"])

with k2:
    st.metric("Football Goals", football_kpis["goals"])

with k3:
    st.metric("F1 Races", f1_kpis["races"])

with k4:
    st.metric("F1 Podiums", f1_kpis["podiums"])

st.divider()

st.subheader("Featured")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Football")
    a, b = st.columns(2)

    with a:
        show_logo_card(
            name="Arsenal",
            subtitle="Featured club",
            image_name="arsenal.png",
            fallback_emoji="⚽",
        )

    with b:
        with st.container(border=True):
            st.markdown("**Top scorer**")
            st.metric(top_scorer["player"], f'{top_scorer["goals"]} goals')
            st.caption(f'xG: {top_scorer["xg"]} | Assists: {top_scorer["assists"]}')

    if st.button("Go to Football →", key="go_football"):
        st.switch_page("pages/1_football.py")

with c2:
    st.markdown("#### Formula 1")
    a, b = st.columns(2)

    with a:
        show_logo_card(
            name="Red Bull Racing",
            subtitle="Featured team",
            image_name="redbull.png",
            fallback_emoji="🏎️",
        )

    with b:
        with st.container(border=True):
            st.markdown("**Top driver**")
            st.metric(top_driver["driver"], f'{top_driver["podiums"]} podiums')
            st.caption("Best podium total in mock dataset")

    st.button("Go to F1 →", key="go_f1", on_click=lambda: st.switch_page("pages/2_f1.py"))

st.divider()

st.subheader("Quick Access")
q1, q2 = st.columns(2)

with q1:
    with st.container(border=True):
        st.markdown("**Football insights**")
        st.write("Team stats, player performance, xG analysis")

with q2:
    with st.container(border=True):
        st.markdown("**F1 insights**")
        st.write("Driver standings, podiums, qualifying vs finish")

st.info("Currently running with mock data while the backend is being built.")
