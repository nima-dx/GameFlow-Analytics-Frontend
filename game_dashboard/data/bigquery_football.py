from data.bigquery_client import get_bq_client
import pandas as pd
import streamlit as st

PROJECT_ID = "le-wagon-data-atelier"
DATASET_ID = "raw_dataset"
TABLE_ID = "seasons"


@st.cache_data(ttl=600)
def seasons_sample() -> pd.DataFrame:
    client = get_bq_client()

    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    """

    return client.query(query).to_dataframe()
