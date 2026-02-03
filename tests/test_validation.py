"""Integration tests for validation and error handling"""
import pytest
import pandas as pd
from utils.validators import validator
from utils.exceptions import ValidationException


class TestValidators:
    """Test validator functions"""
    
    def test_validate_year_valid(self):
        """Test year validation with valid year"""
        year = validator.validate_year(2023)
        assert year == 2023
    
    def test_validate_year_too_old(self):
        """Test year validation rejects old years"""
        with pytest.raises(ValidationException):
            validator.validate_year(1949)
    
    def test_validate_year_future(self):
        """Test year validation rejects distant future"""
        with pytest.raises(ValidationException):
            validator.validate_year(2100)
    
    def test_validate_round_valid(self):
        """Test round validation with valid round"""
        round_num = validator.validate_round_number(5)
        assert round_num == 5
    
    def test_validate_round_invalid_zero(self):
        """Test round validation rejects 0"""
        with pytest.raises(ValidationException):
            validator.validate_round_number(0)
    
    def test_validate_round_exceeds_max(self):
        """Test round validation rejects exceeding max"""
        with pytest.raises(ValidationException):
            validator.validate_round_number(25)
    
    def test_validate_session_type_valid(self):
        """Test session type validation with valid type"""
        session_type = validator.validate_session_type("Race")
        assert session_type == "Race"
    
    def test_validate_session_type_invalid(self):
        """Test session type validation rejects invalid type"""
        with pytest.raises(ValidationException):
            validator.validate_session_type("InvalidSession")
    
    def test_validate_session_type_not_string(self):
        """Test session type validation rejects non-string"""
        with pytest.raises(ValidationException):
            validator.validate_session_type(123)
    
    def test_validate_dataframe_valid(self):
        """Test DataFrame validation with valid DataFrame"""
        df = pd.DataFrame({'A': [1, 2, 3]})
        result = validator.validate_dataframe(df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
    
    def test_validate_dataframe_empty(self):
        """Test DataFrame validation rejects empty"""
        df = pd.DataFrame()
        with pytest.raises(ValidationException):
            validator.validate_dataframe(df)
    
    def test_validate_dataframe_min_rows(self):
        """Test DataFrame validation enforces min rows"""
        df = pd.DataFrame({'A': [1, 2]})
        with pytest.raises(ValidationException):
            validator.validate_dataframe(df, min_rows=5)
    
    def test_validate_driver_abbr_valid(self):
        """Test driver abbreviation validation with valid abbr"""
        driver = validator.validate_driver_abbr("VER")
        assert driver == "VER"
    
    def test_validate_driver_abbr_case_insensitive(self):
        """Test driver abbreviation validation is case-insensitive"""
        driver = validator.validate_driver_abbr("ham")
        assert driver == "HAM"
    
    def test_validate_lap_number_valid(self):
        """Test lap number validation with valid lap"""
        lap = validator.validate_lap_number(42)
        assert lap == 42
    
    def test_validate_lap_number_invalid_zero(self):
        """Test lap number validation rejects 0"""
        with pytest.raises(ValidationException):
            validator.validate_lap_number(0)
    
    def test_validate_lap_number_exceeds_max(self):
        """Test lap number validation enforces max"""
        with pytest.raises(ValidationException):
            validator.validate_lap_number(100, max_laps=50)
    
    def test_validate_telemetry_columns_valid(self):
        """Test telemetry column validation with valid columns"""
        df = pd.DataFrame({
            'Speed': [100, 110, 120],
            'Throttle': [0.5, 0.8, 1.0],
            'Brake': [0, 0.2, 0.5],
            'nGear': [3, 4, 5],
            'Distance': [0, 100, 200]
        })
        result = validator.validate_telemetry_columns(df)
        assert isinstance(result, pd.DataFrame)
    
    def test_validate_telemetry_columns_missing(self):
        """Test telemetry column validation detects missing"""
        df = pd.DataFrame({
            'Speed': [100, 110, 120],
            'Throttle': [0.5, 0.8, 1.0]
        })
        with pytest.raises(ValidationException):
            validator.validate_telemetry_columns(df)


class TestValidationIntegration:
    """Test validation integration across services"""
    
    def test_year_validation_integration(self):
        """Test year validation as part of workflow"""
        # Valid year
        year = validator.validate_year(2024, min_year=2018)
        assert year == 2024
        
        # Out of range
        with pytest.raises(ValidationException):
            validator.validate_year(2017, min_year=2018)
    
    def test_dataframe_telemetry_validation_flow(self):
        """Test DataFrame and telemetry validation flow"""
        # Create valid telemetry
        telemetry = pd.DataFrame({
            'Distance': [0, 100, 200, 300],
            'Speed': [100, 150, 180, 160],
            'Throttle': [0.5, 1.0, 1.0, 0.8],
            'Brake': [0, 0, 0.2, 0.5],
            'nGear': [3, 4, 4, 3]
        })
        
        # Validate as DataFrame
        validated = validator.validate_dataframe(telemetry, "Telemetry", min_rows=1)
        assert len(validated) == 4
        
        # Validate columns
        validated = validator.validate_telemetry_columns(telemetry)
        assert 'Speed' in validated.columns
    
    def test_driver_lap_validation_flow(self):
        """Test driver and lap validation flow"""
        # Valid driver
        driver = validator.validate_driver_abbr("HAM")
        assert driver == "HAM"
        
        # Valid lap
        lap = validator.validate_lap_number(25, max_laps=57)
        assert lap == 25
    
    def test_validation_error_propagation(self):
        """Test that validation errors propagate correctly"""
        # Collect multiple validation errors
        errors = []
        
        # Try invalid year
        try:
            validator.validate_year(1900)
        except ValidationException as e:
            errors.append(str(e))
        
        # Try invalid round
        try:
            validator.validate_round_number(100)
        except ValidationException as e:
            errors.append(str(e))
        
        # Try invalid session
        try:
            validator.validate_session_type("BadSession")
        except ValidationException as e:
            errors.append(str(e))
        
        # Should have 3 errors
        assert len(errors) == 3
        assert all(isinstance(e, str) for e in errors)
