import pandas as pd
import numpy as np

np.random.seed(42)


def get_football_kpis():
    return {
        "matches": 38,
        "goals": 72,
        "xg": 68.4,
        "wins": 22,
    }


def get_team_form_data():
    matchdays = list(range(1, 39))
    goals = np.random.poisson(lam=1.8, size=38)
    xg = np.clip(goals + np.random.normal(0, 0.5, size=38), 0, None)

    points = []
    total = 0

    for g in goals:
        if g >= 2:
            total += 3
        elif g == 1:
            total += 1
        points.append(total)

    return pd.DataFrame({
        "matchday": matchdays,
        "goals": goals,
        "xg": xg.round(2),
        "points": points,
    })


def get_player_stats():
    return pd.DataFrame({
        "player": [
            "Haaland", "Mbappe", "Kane", "Salah",
            "Bellingham", "Vinicius", "Griezmann", "Saka"
        ],
        "goals": [27, 24, 22, 19, 15, 14, 13, 12],
        "xg": [25.3, 21.7, 20.5, 17.2, 12.8, 13.1, 11.4, 10.2],
        "assists": [5, 7, 6, 11, 8, 9, 6, 10],
        "minutes": [2800, 2600, 2750, 2900, 2500, 2400, 2300, 2200],
    })


def get_team_stats():
    return pd.DataFrame({
        "team": ["Arsenal", "Man City", "Liverpool", "Chelsea"],
        "possession": [58, 65, 60, 55],
        "shots": [15.2, 17.8, 16.5, 13.9],
        "pass_accuracy": [87, 90, 88, 85],
        "duels_won": [52, 49, 51, 54],
    })


def get_match_results():
    return pd.DataFrame({
        "date": pd.date_range(start="2025-08-01", periods=10),
        "opponent": [
            "Chelsea", "Liverpool", "Spurs", "Newcastle",
            "Brighton", "Villa", "West Ham", "Everton",
            "Fulham", "Bournemouth"
        ],
        "goals_for": [2, 1, 3, 0, 2, 1, 4, 2, 1, 3],
        "goals_against": [1, 2, 1, 0, 2, 1, 2, 0, 1, 2],
    })

def get_team_season_stats():
    return pd.DataFrame({
        "team": [
            "Arsenal", "Arsenal", "Arsenal", "Arsenal",
            "Chelsea", "Chelsea", "Chelsea", "Chelsea",
            "Liverpool", "Liverpool", "Liverpool", "Liverpool",
            "Man City", "Man City", "Man City", "Man City",
            "Tottenham", "Tottenham", "Tottenham", "Tottenham",
        ],
        "year": [
            2021, 2022, 2023, 2024,
            2021, 2022, 2023, 2024,
            2021, 2022, 2023, 2024,
            2021, 2022, 2023, 2024,
            2021, 2022, 2023, 2024,
        ],
        "points": [
            61, 69, 84, 89,
            67, 74, 44, 63,
            69, 92, 82, 78,
            86, 89, 91, 88,
            62, 71, 66, 70,
        ],
    })
