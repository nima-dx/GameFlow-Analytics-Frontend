import pandas as pd
import numpy as np


def get_f1_kpis():
    return {
        "races": 22,
        "podiums": 66,
        "drivers": 20,
    }


def get_podiums_data():
    data = [
        {"driver": "Max Verstappen", "team": "Red Bull", "podiums": 18},
        {"driver": "Lando Norris", "team": "McLaren", "podiums": 12},
        {"driver": "Charles Leclerc", "team": "Ferrari", "podiums": 10},
        {"driver": "Lewis Hamilton", "team": "Mercedes", "podiums": 9},
        {"driver": "Carlos Sainz", "team": "Ferrari", "podiums": 8},
    ]
    return pd.DataFrame(data)


def get_race_results():
    np.random.seed(42)

    races = [f"Race {i}" for i in range(1, 11)]
    drivers = [
        "Verstappen",
        "Norris",
        "Leclerc",
        "Hamilton",
        "Sainz",
    ]

    data = []

    for race in races:
        for driver in drivers:
            data.append({
                "race": race,
                "driver": driver,
                "position": np.random.randint(1, 6),
                "points": np.random.randint(0, 25),
            })

    return pd.DataFrame(data)


def get_lap_times():
    np.random.seed(42)

    laps = list(range(1, 21))

    data = []

    for lap in laps:
        data.append({
            "lap": lap,
            "Verstappen": 90 + np.random.rand(),
            "Norris": 90 + np.random.rand() + 0.2,
            "Leclerc": 90 + np.random.rand() + 0.4,
        })

    return pd.DataFrame(data)
