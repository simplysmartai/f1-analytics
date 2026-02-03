"""AI Insights tab - Race predictions and analytics"""
import streamlit as st
from typing import Any
import pandas as pd
from utils.logger import logger
from services.ai_service import ai_service
from services.telemetry_service import telemetry_service


def render(session: Any) -> None:
    """
    Render the AI Insights tab.
    
    Args:
        session: FastF1 session object
    """
    try:
        logger.info("Rendering AI Insights tab")
        
        st.markdown("### 🤖 AI Insights & Predictions")
        
        # Determine session type and render appropriate content
        session_type = session.session_type.lower()
        
        if "race" in session_type:
            _render_race_insights(session)
        elif "qualifying" in session_type or "quali" in session_type:
            _render_qualifying_insights(session)
        elif "practice" in session_type:
            _render_practice_insights(session)
        else:
            st.info("Insights not available for this session type")
        
        logger.info("AI Insights tab rendered successfully")
        
    except Exception as e:
        logger.error(f"Error rendering AI Insights tab: {e}")
        st.error(f"Failed to render insights: {e}")


def _render_race_insights(session: Any) -> None:
    """Render race insights and predictions."""
    try:
        st.markdown("#### 🏁 Race Analysis")
        
        # Get qualifying data for race predictions
        try:
            qualifying = session.get_qualifying()
            if qualifying is not None and not qualifying.empty:
                race_predictions = ai_service.predict_race_winner(qualifying)
                
                st.markdown("**Predicted Race Outcome Probabilities:**")
                
                # Create DataFrame for display
                pred_df = pd.DataFrame([
                    {"Driver": driver, "Win Probability": f"{prob*100:.1f}%"}
                    for driver, prob in sorted(race_predictions.items(), key=lambda x: x[1], reverse=True)
                    if prob > 0
                ])
                
                st.dataframe(pred_df, use_container_width=True)
                
                logger.info(f"Displayed race predictions for {len(race_predictions)} drivers")
        
        except Exception as e:
            logger.warning(f"Could not generate race predictions: {e}")
            st.info("Race predictions not available")
        
        # Pit strategy analysis
        try:
            _render_pit_strategy(session)
        except Exception as e:
            logger.warning(f"Pit strategy analysis failed: {e}")
        
        # Driver performance ratings
        _render_driver_performance_ratings(session)
        
    except Exception as e:
        logger.error(f"Error rendering race insights: {e}")
        st.warning("Could not generate race insights")


def _render_qualifying_insights(session: Any) -> None:
    """Render qualifying insights and analysis."""
    try:
        st.markdown("#### 🏎️ Qualifying Analysis")
        
        qualifying = session.get_qualifying()
        if qualifying is None or qualifying.empty:
            st.warning("No qualifying data available")
            return
        
        # Performance rating by grid position
        st.markdown("**Driver Performance Ratings:**")
        
        drivers = session.drivers
        ratings = []
        
        for driver in drivers:
            try:
                driver_laps = telemetry_service.get_driver_laps(session, driver)
                if not driver_laps.empty:
                    rating = ai_service.compute_performance_rating(driver_laps)
                    abbr = session.get_driver(driver)['Abbreviation']
                    ratings.append({"Driver": abbr, "Performance": f"{rating:.1f}/100"})
            except Exception as e:
                logger.debug(f"Could not compute rating for {driver}: {e}")
        
        if ratings:
            ratings_df = pd.DataFrame(ratings).sort_values("Performance", ascending=False)
            st.dataframe(ratings_df, use_container_width=True)
            logger.info(f"Displayed performance ratings for {len(ratings)} drivers")
        else:
            st.info("Performance ratings not available")
        
    except Exception as e:
        logger.error(f"Error rendering qualifying insights: {e}")
        st.warning("Could not generate qualifying insights")


def _render_practice_insights(session: Any) -> None:
    """Render practice session insights."""
    try:
        st.markdown("#### 🛠️ Practice Session Analysis")
        
        drivers = session.drivers
        if len(drivers) == 0:
            st.warning("No driver data available")
            return
        
        st.markdown("**Driver Performance Ratings:**")
        
        ratings = []
        for driver in drivers:
            try:
                driver_laps = telemetry_service.get_driver_laps(session, driver)
                if not driver_laps.empty:
                    rating = ai_service.compute_performance_rating(driver_laps)
                    abbr = session.get_driver(driver)['Abbreviation']
                    ratings.append({"Driver": abbr, "Performance": f"{rating:.1f}/100"})
            except Exception as e:
                logger.debug(f"Could not compute rating for {driver}: {e}")
        
        if ratings:
            ratings_df = pd.DataFrame(ratings).sort_values("Performance", ascending=False)
            st.dataframe(ratings_df, use_container_width=True)
            logger.info(f"Displayed practice ratings for {len(ratings)} drivers")
        else:
            st.info("Performance ratings not available")
        
    except Exception as e:
        logger.error(f"Error rendering practice insights: {e}")
        st.warning("Could not generate practice insights")


def _render_pit_strategy(session: Any) -> None:
    """Render pit strategy analysis."""
    try:
        st.markdown("**Pit Strategy Analysis:**")
        
        strategy = ai_service.analyze_pit_strategy(session)
        
        if strategy:
            st.info("Pit strategy analysis framework ready for expansion")
            logger.info("Pit strategy analysis rendered")
        
    except Exception as e:
        logger.debug(f"Pit strategy analysis not available: {e}")


def _render_driver_performance_ratings(session: Any) -> None:
    """Render performance ratings for all drivers."""
    try:
        st.markdown("**Driver Performance Ratings:**")
        
        drivers = session.drivers
        if len(drivers) == 0:
            return
        
        ratings = []
        for driver in drivers:
            try:
                driver_laps = telemetry_service.get_driver_laps(session, driver)
                if not driver_laps.empty:
                    rating = ai_service.compute_performance_rating(driver_laps)
                    abbr = session.get_driver(driver)['Abbreviation']
                    ratings.append({"Driver": abbr, "Performance": f"{rating:.1f}/100"})
            except Exception as e:
                logger.debug(f"Could not compute rating for {driver}: {e}")
        
        if ratings:
            ratings_df = pd.DataFrame(ratings).sort_values("Performance", ascending=False)
            st.dataframe(ratings_df, use_container_width=True)
            logger.info(f"Displayed performance ratings for {len(ratings)} drivers")
        
    except Exception as e:
        logger.debug(f"Could not render performance ratings: {e}")
