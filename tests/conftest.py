"""Test fixtures and configuration"""
import pytest
import pandas as pd
from datetime import timedelta


@pytest.fixture
def sample_laps_data():
    """Sample lap times data for testing"""
    return pd.DataFrame({
        'LapNumber': [1, 2, 3, 4, 5],
        'LapTime': pd.TimedeltaIndex([
            timedelta(seconds=90.0),
            timedelta(seconds=88.5),
            timedelta(seconds=87.8),
            timedelta(seconds=89.2),
            timedelta(seconds=88.1)
        ]),
        'Driver': ['VER', 'VER', 'VER', 'VER', 'VER'],
        'Abbreviation': ['VER', 'VER', 'VER', 'VER', 'VER']
    })


@pytest.fixture
def sample_quali_data():
    """Sample qualifying results data for testing"""
    return pd.DataFrame({
        'Position': [1, 2, 3],
        'Abbreviation': ['VER', 'HAM', 'LEC'],
        'TeamName': ['Red Bull', 'Mercedes', 'Ferrari']
    })


@pytest.fixture
def sample_schedule():
    """Sample F1 schedule for testing"""
    return pd.DataFrame({
        'RoundNumber': [1, 2, 3],
        'EventName': ['Bahrain', 'Saudi Arabia', 'Australia'],
        'Country': ['Bahrain', 'Saudi Arabia', 'Australia'],
        'EventDate': pd.date_range('2024-01-01', periods=3, freq='W'),
        'Location': ['Sakhir', 'Jeddah', 'Melbourne']
    })
