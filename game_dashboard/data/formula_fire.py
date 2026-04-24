import streamlit as st
from data.bigquery_client import get_bq_client

client = get_bq_client()


@st.cache_data
def load_data_calendar(season):
    query = f"""
        SELECT
            CASE WHEN strStatus = 'Match Finished' THEN 'Completed' ELSE 'Upcoming' END AS Status,
            strEvent AS Event,
            strCountry AS Country,
            CASE
                WHEN strEvent = 'Las Vegas Grand Prix' THEN 'Las Vegas Strip Circuit'
                WHEN strEvent = 'São Paulo Grand Prix' THEN 'Interlagos Circuit'
                ELSE strVenue
            END AS Circuit,
            FORMAT_DATETIME('%-I%p %B %e', DATETIME(strTimestamp)) AS Date
        FROM `le-wagon-data-atelier.analytics_dataset.f1_calendar`
        WHERE EXTRACT(YEAR FROM dateEvent) = {season}
        ORDER BY dateEvent ASC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()



@st.cache_data
def load_data_race_results(season):
    query = f"""
        SELECT
            intPosition,
            strPlayer as Driver,
            strDetail,
            intPoints,
            strEvent,
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results`
        WHERE strSeason = {season}
        LIMIT 1000
    """
    return client.query(query).to_dataframe()


@st.cache_data
def load_data_drivers_championship(season):
    query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(intPoints) DESC) AS Position,
            dr.Driver AS Driver,
            dr.Team,
            dr.Country,
            SUM(intPoints) AS Points
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
        JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
        ON rr.strPlayer = dr.Driver
        WHERE strSeason = {season}
        GROUP BY dr.Driver, dr.Team, dr.Country
        ORDER BY Position ASC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()

def load_data_team_championship(season):
    query = f"""
        SELECT
            ROW_NUMBER() OVER (ORDER BY SUM(intPoints) DESC) AS Position,
            dr.Team,
            SUM(intPoints) AS Points
        FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
        JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
        ON rr.strPlayer = dr.Driver
        WHERE strSeason = {season}
        GROUP BY dr.Team
        ORDER BY Position ASC
        LIMIT 1000
    """
    return client.query(query).to_dataframe()


def point_evolution_drivers(season):

    query = f"""
        WITH race_data AS (
            SELECT
                strEvent AS Event,
                strPlayer AS Driver,
                dr.Team AS Team,
                intPoints AS Points,
                dateEvent AS EventDate
            FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
            JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
                ON rr.strPlayer = dr.Driver
            WHERE strSeason = {season}
        )

        SELECT
            Event,
            EventDate,
            Driver,
            SUM(Points) AS Points_This_Race,
            SUM(SUM(Points)) OVER (
                PARTITION BY Driver
                ORDER BY EventDate
            ) AS Cumulative_Points
        FROM race_data
        GROUP BY Driver, Event, EventDate
        ORDER BY EventDate ASC, Cumulative_Points DESC
    """
    return client.query(query).to_dataframe()

def points_evolution_teams(season):
    query = f"""
        WITH race_data AS (
            SELECT
                strEvent AS Event,
                dr.Team AS Team,
                intPoints AS Points,
                dateEvent AS EventDate
            FROM `le-wagon-data-atelier.analytics_dataset.f1_race_results` rr
            JOIN `le-wagon-data-atelier.raw_dataset.drivers_2026` dr
                ON rr.strPlayer = dr.Driver
            WHERE strSeason = {season}
        )

        SELECT
            Event,
            EventDate,
            Team,
            SUM(Points) AS Points_This_Race,
            SUM(SUM(Points)) OVER (
                PARTITION BY Team
                ORDER BY EventDate
            ) AS Cumulative_Points
        FROM race_data
        GROUP BY Team, Event, EventDate
        ORDER BY EventDate ASC, Cumulative_Points DESC
    """
    return client.query(query).to_dataframe()
