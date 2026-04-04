import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
from timeit import default_timer as timer


# Initialize BigQuery client
credentials = service_account.Credentials.from_service_account_file(
    st.secrets["bigquery"]["credentials_path"]
)
client = bigquery.Client(
    credentials=credentials,
    project=st.secrets["bigquery"]["project_id"]
)
dataset_id = st.secrets["bigquery"]["dataset_id"]
project_id = st.secrets["bigquery"]["project_id"]

TABLES = [
    "races",
    "circuits",
    "constructor_results",
    "constructor_standings",
    "constructors",
    "driver_standings",
    "drivers",
    "lap_times",
    "pit_stops",
    "qualifying",
    "results",
    "seasons",
    "status",
]


# $CHALLENGIFY_BEGIN
@st.cache_data
# $CHALLENGIFY_END
def load_data(table_name):
    """
    Loads the races data from the BigQuery database.
    Implement the right caching decorator.
    Returns:
        pd.DataFrame: The race dataset
    """
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}`"
    data = client.query(query).to_dataframe()

    return data


def create_main_page():
    """
    Creates the following Streamlit headers:
    - A title
    - A subheader
    - A title in the sidebar
    - A markdown section in the sidebar
    - A widget in the sidebar to select a table from the `TABLES` list,
    and then return the selected table (instead of the hard-coded "races" value)
    """
    st.title("Formula 1 Dashboard")
    st.info(
        """
    Delete me once completed
    """
    )
    selected_table = "races"

    # $CHALLENGIFY_BEGIN
    st.subheader("Welcome to the Formula 1 Dashboard")
    st.sidebar.title("Info")
    st.sidebar.markdown("This page shows the Formula 1 data from 1950 to 2020")
    selected_table = st.sidebar.selectbox("Select a table", TABLES, key="table")
    # $CHALLENGIFY_END
    return selected_table


def summary_statistics(data):
    """
    Creates a subheader and writes the summary statistics for the data
    """
    st.subheader("Summary statistics")
    st.info("Use the describe method to get the summary statistics")
    # $CHALLENGIFY_BEGIN
    st.write(data.describe())
    # $CHALLENGIFY_END


@st.cache_data
def top_drivers():
    """timeit
    Get the top 5 drivers with the most points.
    You can get the name from the drivers table and
    combine it with the points from the driver_standings table.
    Returns:
        pd.DataFrame: The top 5 drivers with the columns:
                      - driver_name
                      - total_points
    """
    st.info("Write a query to get the top 5 drivers and visualize the results.")
    # $CHALLENGIFY_BEGIN
    query = f"""
    SELECT
        CONCAT(forename,' ',surname) as driver_name,
        SUM(points) as total_points
    FROM
        `{project_id}.{dataset_id}.drivers`
    INNER JOIN
        `{project_id}.{dataset_id}.driver_standings` ON drivers.driver_id = driver_standings.driver_id
    GROUP BY
        CONCAT(forename,' ',surname)
    ORDER BY
        SUM(points) DESC
    LIMIT
        5
    """
    top_drivers = client.query(query).to_dataframe()
    return top_drivers
    # $CHALLENGIFY_END


@st.cache_data
def lewis_over_the_years():
    """
    Get the points from Lewis Hamilton between 2007 and 2018.
    Use the following table to get the data:
        - drivers
        - driver_standings
        - races

    Returns:
        pd.DataFrame: The points from Lewis Hamilton over the years, with the columns:
                        - year
                        - total_points
    """
    st.info(
        "Write a query to get the points of Lewis Hamilton over the years and visualize the results."
    )
    # $CHALLENGIFY_BEGIN
    query = f"""
    WITH lewis_id AS (
        SELECT driver_id FROM `{project_id}.{dataset_id}.drivers` WHERE surname = 'Hamilton' AND forename = 'Lewis'
    ),

    driver_points AS (
        SELECT points, race_id, driver_id FROM `{project_id}.{dataset_id}.driver_standings`
    ),

    race_results AS (
        SELECT race_id, year FROM `{project_id}.{dataset_id}.races`
    )

    SELECT
        year, MAX(points) as total_points
    FROM
        lewis_id
    INNER JOIN
        driver_points
    ON
        lewis_id.driver_id = driver_points.driver_id
    INNER JOIN
        race_results ON race_results.race_id = driver_points.race_id
    WHERE year > 2006
    GROUP BY
        year
    """
    lewis_points = client.query(query).to_dataframe()
    return lewis_points
    # $CHALLENGIFY_END


def session_state(data):
    """
    Initialize the session state
    using data as the key and value as the
    initialization value.

    Put data in the session state after having
    initialized it.

    Args:
        data (pd.DataFrame): The formula 1 dataset
    """

    # Initialization of session state, assign a random value
    # to the session state
    # $CHALLENGIFY_BEGIN
    if "data" not in st.session_state:
        st.session_state["data"] = "value"
    # $CHALLENGIFY_END

    # Update the session state using the dataframe
    # $CHALLENGIFY_BEGIN
    st.session_state["data"] = data
    # $CHALLENGIFY_END


if __name__ == "__main__":
    selected_table = create_main_page()

    # used to time the loading of the data
    start = timer()
    data = load_data(selected_table)
    end = timer()
    st.sidebar.info(f"{round(end-start,4)} seconds to load the data")

    st.dataframe(data)

    summary_statistics(data)
    session_state(data)

    st.subheader("Top 5 Drivers")
    top_driver_data = top_drivers()
    st.write(top_driver_data)
    st.warning("Use the Altair library to create a bar chart with the top drivers")
    # create a bar chart with the top drivers
    # $CHALLENGIFY_BEGIN
    bar_chart = (
        alt.Chart(top_driver_data)
        .mark_bar()
        .encode(
            y=alt.Y("total_points"),
            x=alt.X("driver_name", sort="-y"),
            color="driver_name",
            tooltip="total_points",
        )
    )

    st.altair_chart(bar_chart, use_container_width=True)
    # $CHALLENGIFY_END

    st.subheader("Lewis Hamilton over the years")
    lewis_years = lewis_over_the_years()

    # Convert the year column to datetime
    lewis_years["year"] = pd.to_datetime(lewis_years["year"], format="%Y")

    st.warning("Create a line chart with the lewis_years, use the Altair library")
    # $CHALLENGIFY_BEGIN
    line_chart = alt.Chart(lewis_years).mark_line().encode(y="total_points", x="year")

    st.altair_chart(line_chart, use_container_width=True)
    # $CHALLENGIFY_END
