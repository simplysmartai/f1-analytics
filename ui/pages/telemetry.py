"""Telemetry tab - Telemetry data visualization"""
import streamlit as st
from typing import Any, Optional
from utils.logger import logger
from services.telemetry_service import telemetry_service


def render(session: Any) -> None:
    """
    Render the Telemetry tab.
    
    Args:
        session: FastF1 session object
    """
    try:
        logger.info("Rendering Telemetry tab")
        
        st.markdown("### 📡 Telemetry Data")
        
        # Get available drivers
        drivers = session.drivers
        if len(drivers) == 0:
            st.warning("No drivers available for this session")
            return
        
        driver_info = {session.get_driver(d)['Abbreviation']: d for d in drivers}
        
        # Driver selection
        selected_driver = st.selectbox("Select Driver", options=list(driver_info.keys()))
        
        if selected_driver:
            _render_telemetry(session, selected_driver)
        
        logger.info("Telemetry tab rendered successfully")
        
    except Exception as e:
        logger.error(f"Error rendering Telemetry tab: {e}")
        st.error(f"Failed to render telemetry: {e}")


def _render_telemetry(session: Any, driver: str) -> None:
    """Render telemetry for a selected driver and lap."""
    try:
        # Get driver laps
        driver_laps = telemetry_service.get_driver_laps(session, driver)
        
        if driver_laps.empty:
            st.warning(f"No lap data available for {driver}")
            return
        
        # Lap selection
        lap_options = sorted(driver_laps['LapNumber'].dropna().unique())
        if len(lap_options) == 0:
            st.warning("No valid lap numbers found")
            return
        
        selected_lap_num = st.selectbox("Select Lap", options=lap_options)
        
        if selected_lap_num:
            lap = driver_laps[driver_laps['LapNumber'] == selected_lap_num].iloc[0]
            
            try:
                # Get telemetry for the lap
                telemetry = lap.get_telemetry()
                
                # Speed trace
                st.markdown("#### 🏁 Speed Trace")
                fig_speed = telemetry_service.create_speed_trace(telemetry, driver, int(selected_lap_num))
                st.plotly_chart(fig_speed, use_container_width=True)
                
                # Throttle and Brake
                st.markdown("#### 🎛️ Throttle & Brake")
                fig_controls = telemetry_service.create_controls_chart(telemetry)
                st.plotly_chart(fig_controls, use_container_width=True)
                
                # Gear changes
                st.markdown("#### ⚙️ Gear Usage")
                import plotly.express as px
                fig_gear = px.line(
                    telemetry,
                    x='Distance',
                    y='nGear',
                    title="Gear Selection"
                )
                fig_gear.update_yaxis(title="Gear", dtick=1)
                fig_gear.update_xaxis(title="Distance (m)")
                st.plotly_chart(fig_gear, use_container_width=True)
                
                logger.info(f"Rendered telemetry for {driver} lap {selected_lap_num}")
                
            except Exception as e:
                logger.warning(f"Telemetry data not available for lap {selected_lap_num}: {e}")
                st.warning(f"Telemetry data not available for this lap: {e}")
    
    except Exception as e:
        logger.error(f"Failed to render telemetry for {driver}: {e}")
        st.warning(f"Could not load telemetry: {e}")
