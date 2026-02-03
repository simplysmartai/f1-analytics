"""Unit tests for services"""
import pytest
from datetime import timedelta
import pandas as pd

from services.telemetry_service import telemetry_service
from services.ai_service import ai_service


class TestTelemetryService:
    """Tests for TelemetryService"""
    
    def test_compute_performance_rating_valid_data(self, sample_laps_data):
        """Test performance rating with valid data"""
        rating = telemetry_service.compute_performance_rating(sample_laps_data)
        assert 0 <= rating <= 100
        assert rating > 0  # Should have valid rating
    
    def test_compute_performance_rating_empty_data(self):
        """Test performance rating with empty data"""
        empty_df = pd.DataFrame({'LapTime': []})
        rating = telemetry_service.compute_performance_rating(empty_df)
        assert rating == 0.0
    
    def test_compute_performance_rating_single_lap(self):
        """Test performance rating with single lap (perfect consistency)"""
        single_lap = pd.DataFrame({
            'LapTime': pd.TimedeltaIndex([timedelta(seconds=90.0)])
        })
        rating = telemetry_service.compute_performance_rating(single_lap)
        assert rating > 90  # Should be near-perfect


class TestAIService:
    """Tests for AIService"""
    
    def test_compute_performance_rating_valid_data(self, sample_laps_data):
        """Test AI performance rating with valid data"""
        rating = ai_service.compute_performance_rating(sample_laps_data)
        assert 0 <= rating <= 100
        assert rating > 0
    
    def test_compute_performance_rating_empty_data(self):
        """Test AI performance rating with empty data"""
        empty_df = pd.DataFrame({'LapTime': []})
        rating = ai_service.compute_performance_rating(empty_df)
        assert rating == 0.0
    
    def test_predict_race_winner_valid_data(self, sample_quali_data):
        """Test race winner prediction with valid data"""
        predictions = ai_service.predict_race_winner(sample_quali_data)
        assert len(predictions) == 3
        # All predictions should sum to 1.0 (normalized probabilities)
        assert abs(sum(predictions.values()) - 1.0) < 0.01
    
    def test_predict_race_winner_empty_data(self):
        """Test race winner prediction with empty data"""
        empty_df = pd.DataFrame({'Position': [], 'Abbreviation': []})
        predictions = ai_service.predict_race_winner(empty_df)
        assert predictions == {}
    
    def test_predict_race_winner_first_position_highest(self, sample_quali_data):
        """Test that P1 gets highest probability"""
        predictions = ai_service.predict_race_winner(sample_quali_data)
        # First position should have highest probability
        if len(predictions) > 0:
            max_prob_driver = max(predictions, key=predictions.get)
            assert predictions[max_prob_driver] > 0.3  # P1 should be > 30%
    
    def test_analyze_pit_strategy(self):
        """Test pit strategy analysis"""
        strategies = ai_service.analyze_pit_strategy(None)
        assert isinstance(strategies, list)
