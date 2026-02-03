"""Sidebar component for race selection"""
import streamlit as st
from typing import Optional, Tuple
from datetime import datetime
import pandas as pd

from config.settings import settings
from services.f1_data_service import data_service
from utils.logger import logger


class SidebarComponent:
    """Sidebar for race and session selection"""
    
    @staticmethod
    def render() -> Optional[Tuple[int, str, int]]:
        """
        Render sidebar and return selections.
        
        Returns:
            Tuple of (year, session_type, round_number) or None if error
        """
        with st.sidebar:
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1200px-F1.svg.png",
                width=150
            )
            st.markdown("## 🏁 Select Race")
            
            # Year selection
            current_year = datetime.now().year
            year = st.selectbox(
                "Season",
                options=list(range(current_year, settings.FASTF1_SEASON_START - 1, -1)),
                index=0 if current_year <= 2025 else 1
            )
            
            # Session type selection (from settings)
            session_type = st.radio(
                "Session Type",
                options=list(settings.SESSION_TYPES.keys()),
                index=0
            )
            
            st.markdown("---")
            st.markdown("### About")
            st.markdown("""
            Built on [F1 Race Replay](https://github.com/IAmTomShaw/f1-race-replay)
            by Tom Shaw.
            
            Enhanced with AI analytics by **nexairi.com**
            """)
        
        # Load schedule
        try:
            logger.info(f"Loading schedule for {year}")
            schedule = data_service.get_schedule(year)
            
            if schedule is None or len(schedule) == 0:
                logger.warning(f"No schedule available for {year}")
                st.warning(f"No races available yet for {year}")
                return None
            
            # Get available races (past/current)
            today = pd.Timestamp.now()
            available_races = schedule[schedule['EventDate'] <= today]
            
            if len(available_races) == 0:
                logger.warning(f"No past races in {year}")
                st.warning(f"No races available yet for {year}")
                return None
            
            # Race selection
            with st.sidebar:
                race_options = {
                    f"Round {int(row['RoundNumber'])}: {row['EventName']} ({row['Country']})": 
                    int(row['RoundNumber'])
                    for _, row in available_races.iterrows()
                }
                
                selected_race = st.selectbox(
                    "Grand Prix",
                    options=list(race_options.keys())
                )
                round_number = race_options[selected_race]
            
            logger.info(f"Selected: {session_type} at R{round_number}/{year}")
            return year, session_type, round_number
            
        except Exception as e:
            logger.error(f"Sidebar error: {e}")
            st.error(f"Failed to load race data: {e}")
            return None
