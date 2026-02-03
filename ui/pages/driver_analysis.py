"""Driver Analysis tab - Lap time comparison and statistics"""
import streamlit as st
import pandas as pd
from typing import Any
from utils.logger import logger
from services.telemetry_service import telemetry_service
from services.ai_service import ai_service


def render(session: Any) -> None:
    """
    Render the Driver Analysis tab.
    
    Args:
        session: FastF1 session object
    """
    try:
        logger.info("Rendering Driver Analysis tab")
        
        st.markdown("### 🏎️ Compare Drivers")
        
        # Get available drivers
        drivers = session.drivers
        if len(drivers) == 0:
            st.warning("No drivers available for this session")
            return
        
        driver_info = {session.get_driver(d)['Abbreviation']: d for d in drivers}
        
        # Driver selection
        col1, col2 = st.columns(2)
        
        with col1:
            driver1 = st.selectbox("Driver 1", options=list(driver_info.keys()), index=0)
        with col2:
            driver2 = st.selectbox(
                "Driver 2",
                options=list(driver_info.keys()),
                index=1 if len(driver_info) > 1 else 0
            )
        
        if driver1 and driver2:
            _render_comparison(session, driver1, driver2)
        
        logger.info("Driver Analysis tab rendered successfully")
        
    except Exception as e:
        logger.error(f"Error rendering Driver Analysis tab: {e}")
        st.error(f"Failed to render driver analysis: {e}")


def _render_comparison(session: Any, driver1: str, driver2: str) -> None:
    """Render lap time comparison between two drivers."""
    try:
        # Get driver laps
        driver1_laps = telemetry_service.get_driver_laps(session, driver1)
        driver2_laps = telemetry_service.get_driver_laps(session, driver2)
        
        if driver1_laps.empty or driver2_laps.empty:
            st.warning("No lap data available for one or both drivers")
            return
        
        # Lap time comparison chart
        st.markdown("#### ⏱️ Lap Time Comparison")
        fig = telemetry_service.create_lap_comparison_chart(
            driver1_laps, driver2_laps, driver1, driver2
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{driver1} Stats**")
            _render_driver_stats(driver1_laps, driver1, ai_service)
        
        with col2:
            st.markdown(f"**{driver2} Stats**")
            _render_driver_stats(driver2_laps, driver2, ai_service)
        
        logger.info(f"Rendered comparison between {driver1} and {driver2}")
        
    except Exception as e:
        logger.error(f"Failed to render comparison: {e}")
        st.warning(f"Could not compare drivers: {e}")


def _render_driver_stats(laps: pd.DataFrame, driver: str, ai_service: Any) -> None:
    """Render statistics for a single driver."""
    try:
        if laps.empty:
            st.metric("Status", "No data")
            return
        
        fastest_lap = laps['LapTime'].min()
        avg_lap = laps['LapTime'].mean()
        rating = ai_service.compute_performance_rating(laps)
        
        col1, col2 = st.columns(2)
        with col1:
            if pd.notna(fastest_lap):
                st.metric("Fastest Lap", str(fastest_lap).split()[-1])
            else:
                st.metric("Fastest Lap", "N/A")
        
        with col2:
            if pd.notna(avg_lap):
                st.metric("Average Lap", str(avg_lap).split()[-1])
            else:
                st.metric("Average Lap", "N/A")
        
        st.metric("Performance Rating", f"{rating:.1f} / 100")
        
    except Exception as e:
        logger.error(f"Failed to render driver stats for {driver}: {e}")
        st.metric("Status", "Error loading stats")
