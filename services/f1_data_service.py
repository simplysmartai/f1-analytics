"""FastF1 data operations"""
import fastf1
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any
import streamlit as st

from config.settings import settings
from utils.logger import logger
from utils.exceptions import DataLoadException, CacheException, ValidationException
from utils.validators import validator
from utils.performance import monitor_performance

class F1DataService:
    """Service for FastF1 data operations"""
    
    def __init__(self):
        self._initialize_cache()
    
    def _initialize_cache(self) -> None:
        """Initialize FastF1 caching"""
        try:
            settings.CACHE_DIR.mkdir(exist_ok=True)
            fastf1.Cache.enable_cache(str(settings.CACHE_DIR))
            logger.info(f"Cache enabled at {settings.CACHE_DIR}")
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise CacheException(f"Cache initialization failed: {e}")
    
    @st.cache_data(ttl=settings.CACHE_SCHEDULE_TTL)
    @monitor_performance("get_schedule")
    def get_schedule(self, year: int) -> Optional[pd.DataFrame]:
        """
        Fetch F1 schedule for given year.
        
        Args:
            year: F1 season year
            
        Returns:
            DataFrame with available races
            
        Raises:
            DataLoadException: If schedule cannot be loaded
            ValidationException: If year is invalid
        """
        try:
            # Validate input
            year = validator.validate_year(year)
            
            logger.info(f"Fetching schedule for {year}")
            schedule = fastf1.get_event_schedule(year)
            
            # Validate result
            schedule = validator.validate_dataframe(schedule, "Schedule")
            
            # Filter to past/current races
            today = pd.Timestamp.now()
            available = schedule[schedule['EventDate'] <= today]
            
            if available.empty:
                logger.warning(f"No races available yet for {year}")
                return available
            
            logger.info(f"Found {len(available)} available races in {year}")
            return available
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to load schedule for {year}: {e}")
            raise DataLoadException(f"Cannot load schedule: {e}") from e
    
    @st.cache_data(ttl=settings.CACHE_SESSION_TTL)
    @monitor_performance("get_session")
    def get_session(self, year: int, round_num: int, session_type: str) -> Optional[Any]:
        """
        Fetch F1 session data.
        
        Args:
            year: F1 season year
            round_num: Race round number
            session_type: Type of session (Race, Qualifying, etc)
            
        Returns:
            FastF1 session object
            
        Raises:
            DataLoadException: If session cannot be loaded
            ValidationException: If inputs are invalid
        """
        try:
            # Validate inputs
            year = validator.validate_year(year)
            round_num = validator.validate_round_number(round_num)
            session_type = validator.validate_session_type(session_type)
            
            logger.info(f"Fetching {session_type} session for R{round_num}/{year}")
            session = fastf1.get_session(year, round_num, session_type)
            
            if session is None:
                raise DataLoadException(f"Session not found for R{round_num}/{year}")
            
            session.load()
            
            # Validate session object
            validator.validate_session_object(session)
            
            logger.info(f"Successfully loaded session for R{round_num}/{year}")
            return session
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            raise DataLoadException(f"Cannot load session: {e}") from e
    
    def get_session_results(self, session: Any) -> pd.DataFrame:
        """Extract results from session"""
        try:
            return pd.DataFrame({
                'Position': session.results['Position'],
                'Driver': session.results['Abbreviation'],
                'Team': session.results['TeamName'],
                'Time': session.results['Time'],
                'Status': session.results['Status'],
                'Points': session.results['Points']
            })
        except Exception as e:
            logger.error(f"Failed to extract results: {e}")
            raise DataLoadException(f"Cannot extract results: {e}")

# Singleton
data_service = F1DataService()
