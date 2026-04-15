import streamlit as st
import plotly.express as px


def line_chart(df, x, y, title, color=None):
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(df, x, y, title, color=None):
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    st.plotly_chart(fig, use_container_width=True)


def scatter_chart(df, x, y, title, color=None, size=None):
    fig = px.scatter(df, x=x, y=y, color=color, size=size, title=title)
    st.plotly_chart(fig, use_container_width=True)
