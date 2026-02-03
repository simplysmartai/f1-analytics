"""Overview tab - Session information and results"""
import streamlit as st
import pandas as pd
from typing import Any
from utils.logger import logger


def render(session: Any, session_type: str) -> None:
    """
    Render the Overview tab.
    
    Args:
        session: FastF1 session object
        session_type: Type of session (Race, Qualifying, etc.)
    """
    try:
        logger.info("Rendering Overview tab")
        
        # Display event information
        col1, col2, col3, col4 = st.columns(4)
        event_info = session.event
        
        with col1:
            st.metric("🏁 Event", event_info['EventName'])
        with col2:
            st.metric("📍 Location", event_info['Location'])
        with col3:
            st.metric("📅 Date", event_info['EventDate'].strftime('%Y-%m-%d'))
        with col4:
            st.metric("🔢 Round", int(event_info['RoundNumber']))
        
        st.markdown("### 🏆 Session Results")
        
        # Display results based on session type
        if session_type in ["Race", "Sprint"]:
            _render_race_results(session)
        elif session_type in ["Qualifying", "Sprint Qualifying"]:
            _render_qualifying_results(session)
        else:
            _render_practice_results(session)
            
        logger.info("Overview tab rendered successfully")
        
    except Exception as e:
        logger.error(f"Error rendering Overview tab: {e}")
        st.error(f"Failed to render overview: {e}")


def _render_race_results(session: Any) -> None:
    """Render race session results."""
    try:
        results = session.results
        results_df = pd.DataFrame({
            'Position': results['Position'].astype(int),
            'Driver': results['Abbreviation'],
            'Team': results['TeamName'],
            'Time': results['Time'],
            'Status': results['Status'],
            'Points': results['Points'].astype(int)
        })
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    except Exception as e:
        logger.error(f"Failed to render race results: {e}")
        st.warning("Could not load race results")


def _render_qualifying_results(session: Any) -> None:
    """Render qualifying session results."""
    try:
        results = session.results
        results_df = pd.DataFrame({
            'Position': results['Position'].astype(int),
            'Driver': results['Abbreviation'],
            'Team': results['TeamName'],
            'Q1': results['Q1'],
            'Q2': results['Q2'],
            'Q3': results['Q3']
        })
        st.dataframe(results_df, use_container_width=True, hide_index=True)
    except Exception as e:
        logger.error(f"Failed to render qualifying results: {e}")
        st.warning("Could not load qualifying results")


def _render_practice_results(session: Any) -> None:
    """Render practice session results (if available)."""
    try:
        if hasattr(session, 'results') and len(session.results) > 0:
            results = session.results
            results_df = pd.DataFrame({
                'Position': results['Position'].astype(int),
                'Driver': results['Abbreviation'],
                'Team': results['TeamName'],
                'Time': results['Time'],
                'Gap': results['Gap']
            })
            st.dataframe(results_df, use_container_width=True, hide_index=True)
        else:
            st.info("No results available for this practice session")
    except Exception as e:
        logger.error(f"Failed to render practice results: {e}")
        st.info("Results not available for this session")
