import streamlit as st
from google.cloud import bigquery

@st.cache_resource
def get_bq_client():
    return bigquery.Client()
