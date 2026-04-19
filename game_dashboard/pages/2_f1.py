import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

# Connect
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project="le-wagon-data-atelier")

# Query your analytics_dataset
@st.cache_data
def load_data(query):
    return client.query(query).to_dataframe()

df = load_data("""
    SELECT * FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results`
    LIMIT 1000
""")

st.dataframe(df)
