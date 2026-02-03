"""Input and data validation utilities"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
from utils.exceptions import ValidationException
from utils.logger import logger


class Validator:
    """Centralized validation for user inputs and data"""
    
    @staticmethod
    def validate_year(year: int, min_year: int = 2018, max_year: Optional[int] = None) -> int:
        """
        Validate F1 season year.
        
        Args:
            year: Year to validate
            min_year: Minimum allowed year (default 2018 for modern F1)
            max_year: Maximum allowed year (default current year)
            
        Returns:
            Validated year
            
        Raises:
            ValidationException: If year is invalid
        """
        if max_year is None:
            max_year = datetime.now().year
        
        try:
            year_int = int(year)
            
            if year_int < min_year or year_int > max_year:
                raise ValidationException(
                    f"Year must be between {min_year} and {max_year}, got {year_int}"
                )
            
            logger.debug(f"Year validation passed: {year_int}")
            return year_int
            
        except (TypeError, ValueError) as e:
            raise ValidationException(f"Invalid year format: {e}") from e
    
    @staticmethod
    def validate_round_number(round_num: Union[int, float], max_rounds: int = 24) -> int:
        """
        Validate F1 race round number.
        
        Args:
            round_num: Round number to validate
            max_rounds: Maximum rounds in season (default 24)
            
        Returns:
            Validated round number
            
        Raises:
            ValidationException: If round number is invalid
        """
        try:
            round_int = int(round_num)
            
            if round_int < 1 or round_int > max_rounds:
                raise ValidationException(
                    f"Round number must be between 1 and {max_rounds}, got {round_int}"
                )
            
            logger.debug(f"Round validation passed: {round_int}")
            return round_int
            
        except (TypeError, ValueError) as e:
            raise ValidationException(f"Invalid round number format: {e}") from e
    
    @staticmethod
    def validate_session_type(session_type: str, valid_types: Optional[List[str]] = None) -> str:
        """
        Validate F1 session type.
        
        Args:
            session_type: Session type to validate
            valid_types: List of valid session types
            
        Returns:
            Validated session type
            
        Raises:
            ValidationException: If session type is invalid
        """
        if valid_types is None:
            valid_types = ["Race", "Sprint", "Qualifying", "Sprint Qualifying", "Practice 1", "Practice 2", "Practice 3"]
        
        if not isinstance(session_type, str):
            raise ValidationException(f"Session type must be string, got {type(session_type)}")
        
        session_type = session_type.strip()
        
        if session_type not in valid_types:
            raise ValidationException(
                f"Invalid session type '{session_type}'. Valid types: {', '.join(valid_types)}"
            )
        
        logger.debug(f"Session type validation passed: {session_type}")
        return session_type
    
    @staticmethod
    def validate_dataframe(df: Optional[Any], name: str = "DataFrame", min_rows: int = 0) -> pd.DataFrame:
        """
        Validate that data is a valid non-empty DataFrame.
        
        Args:
            df: Object to validate
            name: Name for error messages
            min_rows: Minimum required rows
            
        Returns:
            Validated DataFrame
            
        Raises:
            ValidationException: If DataFrame is invalid or empty
        """
        if df is None:
            raise ValidationException(f"{name} is None")
        
        if not isinstance(df, pd.DataFrame):
            raise ValidationException(f"{name} must be DataFrame, got {type(df)}")
        
        if df.empty:
            raise ValidationException(f"{name} is empty")
        
        if len(df) < min_rows:
            raise ValidationException(
                f"{name} has only {len(df)} rows, minimum required: {min_rows}"
            )
        
        logger.debug(f"{name} validation passed: {len(df)} rows, {len(df.columns)} columns")
        return df
    
    @staticmethod
    def validate_driver_abbr(driver: str, valid_drivers: Optional[List[str]] = None) -> str:
        """
        Validate driver abbreviation.
        
        Args:
            driver: Driver abbreviation to validate
            valid_drivers: List of valid driver abbreviations (optional)
            
        Returns:
            Validated driver abbreviation
            
        Raises:
            ValidationException: If driver is invalid
        """
        if not isinstance(driver, str):
            raise ValidationException(f"Driver must be string, got {type(driver)}")
        
        driver = driver.strip().upper()
        
        if len(driver) != 3:
            logger.warning(f"Driver abbreviation unusual length: {driver}")
        
        if valid_drivers and driver not in valid_drivers:
            raise ValidationException(
                f"Unknown driver: {driver}. Valid drivers: {', '.join(valid_drivers[:5])}..."
            )
        
        logger.debug(f"Driver validation passed: {driver}")
        return driver
    
    @staticmethod
    def validate_lap_number(lap_num: Union[int, float], max_laps: Optional[int] = None) -> int:
        """
        Validate lap number.
        
        Args:
            lap_num: Lap number to validate
            max_laps: Maximum laps in session (optional)
            
        Returns:
            Validated lap number
            
        Raises:
            ValidationException: If lap number is invalid
        """
        try:
            lap_int = int(lap_num)
            
            if lap_int < 1:
                raise ValidationException(f"Lap number must be >= 1, got {lap_int}")
            
            if max_laps and lap_int > max_laps:
                raise ValidationException(
                    f"Lap {lap_int} exceeds maximum {max_laps} laps"
                )
            
            logger.debug(f"Lap number validation passed: {lap_int}")
            return lap_int
            
        except (TypeError, ValueError) as e:
            raise ValidationException(f"Invalid lap number format: {e}") from e
    
    @staticmethod
    def validate_telemetry_columns(telemetry: pd.DataFrame, required_cols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Validate telemetry DataFrame has required columns.
        
        Args:
            telemetry: Telemetry DataFrame to validate
            required_cols: Required column names (default: Speed, Throttle, Brake, nGear)
            
        Returns:
            Validated DataFrame
            
        Raises:
            ValidationException: If required columns are missing
        """
        if required_cols is None:
            required_cols = ['Speed', 'Throttle', 'Brake', 'nGear', 'Distance']
        
        telemetry = Validator.validate_dataframe(telemetry, "Telemetry")
        
        missing_cols = [col for col in required_cols if col not in telemetry.columns]
        
        if missing_cols:
            available = list(telemetry.columns)[:5]
            raise ValidationException(
                f"Telemetry missing columns: {', '.join(missing_cols)}. "
                f"Available: {', '.join(available)}..."
            )
        
        logger.debug(f"Telemetry columns validation passed")
        return telemetry
    
    @staticmethod
    def validate_session_object(session: Any) -> bool:
        """
        Validate that object is a valid FastF1 session.
        
        Args:
            session: Object to validate
            
        Returns:
            True if valid session
            
        Raises:
            ValidationException: If session is invalid
        """
        if session is None:
            raise ValidationException("Session is None")
        
        required_attrs = ['drivers', 'event', 'session_type', 'laps', 'results']
        
        for attr in required_attrs:
            if not hasattr(session, attr):
                raise ValidationException(f"Session missing required attribute: {attr}")
        
        logger.debug(f"Session object validation passed")
        return True


# Global validator instance
validator = Validator()
