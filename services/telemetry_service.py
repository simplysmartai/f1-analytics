"""Telemetry analysis operations"""
import pandas as pd
from typing import Optional, Any
import plotly.graph_objects as go
import plotly.express as px
from utils.logger import logger
from utils.validators import validator
from utils.exceptions import ValidationException
from utils.performance import monitor_performance


class TelemetryService:
    """Service for telemetry analysis"""
    
    @staticmethod
    @monitor_performance("get_driver_laps")
    def get_driver_laps(session: Any, driver: str) -> pd.DataFrame:
        """
        Get all laps for a driver.
        
        Args:
            session: FastF1 session object
            driver: Driver abbreviation (e.g., 'VER')
            
        Returns:
            DataFrame with driver's lap data
            
        Raises:
            ValidationException: If inputs are invalid
        """
        try:
            # Validate inputs
            validator.validate_session_object(session)
            validator.validate_driver_abbr(driver)
            
            logger.info(f"Fetching laps for driver {driver}")
            laps = session.laps.pick_driver(driver)
            
            if laps.empty:
                logger.warning(f"No laps found for driver {driver}")
                return laps
            
            logger.info(f"Found {len(laps)} laps for {driver}")
            return laps
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to get driver laps for {driver}: {e}")
            raise
    
    @staticmethod
    @monitor_performance("create_lap_comparison_chart")
    def create_lap_comparison_chart(
        driver1_laps: pd.DataFrame,
        driver2_laps: pd.DataFrame,
        driver1_name: str,
        driver2_name: str
    ) -> go.Figure:
        """
        Create lap time comparison chart.
        
        Args:
            driver1_laps: First driver's lap data
            driver2_laps: Second driver's lap data
            driver1_name: First driver name/abbreviation
            driver2_name: Second driver name/abbreviation
            
        Returns:
            Plotly figure object
            
        Raises:
            ValidationException: If inputs are invalid
        """
        try:
            # Validate inputs
            driver1_laps = validator.validate_dataframe(driver1_laps, "Driver 1 laps", min_rows=1)
            driver2_laps = validator.validate_dataframe(driver2_laps, "Driver 2 laps", min_rows=1)
            
            validator.validate_driver_abbr(driver1_name)
            validator.validate_driver_abbr(driver2_name)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=driver1_laps['LapNumber'],
                y=driver1_laps['LapTime'].dt.total_seconds(),
                mode='lines+markers',
                name=driver1_name,
                line=dict(width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=driver2_laps['LapNumber'],
                y=driver2_laps['LapTime'].dt.total_seconds(),
                mode='lines+markers',
                name=driver2_name,
                line=dict(width=2)
            ))
            
            fig.update_layout(
                xaxis_title="Lap Number",
                yaxis_title="Lap Time (seconds)",
                hovermode='x unified',
                height=400
            )
            
            logger.info("Lap comparison chart created")
            return fig
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to create comparison chart: {e}")
            raise
    
    @staticmethod
    @monitor_performance("create_speed_trace")
    def create_speed_trace(telemetry: pd.DataFrame, driver: str, lap_num: int) -> go.Figure:
        """
        Create speed trace chart.
        
        Args:
            telemetry: Telemetry data for the lap
            driver: Driver abbreviation
            lap_num: Lap number
            
        Returns:
            Plotly figure object
            
        Raises:
            ValidationException: If inputs are invalid
        """
        try:
            # Validate inputs
            telemetry = validator.validate_telemetry_columns(telemetry, ['Distance', 'Speed'])
            validator.validate_driver_abbr(driver)
            validator.validate_lap_number(lap_num)
            
            logger.info(f"Creating speed trace for {driver} lap {lap_num}")
            fig = px.line(telemetry, x='Distance', y='Speed',
                         title=f"{driver} - Lap {lap_num} Speed")
            fig.update_xaxis(title="Distance (m)")
            fig.update_yaxis(title="Speed (km/h)")
            return fig
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to create speed trace: {e}")
            raise
    
    @staticmethod
    @monitor_performance("create_controls_chart")
    def create_controls_chart(telemetry: pd.DataFrame) -> go.Figure:
        """
        Create throttle and brake input chart.
        
        Args:
            telemetry: Telemetry data for the lap
            
        Returns:
            Plotly figure object
            
        Raises:
            ValidationException: If telemetry is invalid
        """
        try:
            # Validate input
            telemetry = validator.validate_telemetry_columns(telemetry, ['Distance', 'Throttle', 'Brake'])
            
            logger.info("Creating throttle/brake chart")
            fig = go.Figure()
        
            fig.add_trace(go.Scatter(
                x=telemetry['Distance'],
                y=telemetry['Throttle'],
                mode='lines',
                name='Throttle',
                fill='tozeroy',
                line=dict(color='green')
            ))
            
            fig.add_trace(go.Scatter(
                x=telemetry['Distance'],
                y=telemetry['Brake'],
                mode='lines',
                name='Brake',
                fill='tozeroy',
                line=dict(color='red')
            ))
            
            fig.update_xaxis(title="Distance (m)")
            fig.update_yaxis(title="Input (%)")
            return fig
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to create controls chart: {e}")
            raise
    
    @staticmethod
    @monitor_performance("compute_performance_rating")
    def compute_performance_rating(driver_laps: pd.DataFrame) -> float:
        """
        Compute driver performance rating (0-100).
        
        Args:
            driver_laps: DataFrame with lap times
            
        Returns:
            Performance rating from 0 to 100
            
        Raises:
            ValidationException: If input is invalid
        """
        try:
            # Validate input (allow empty for graceful degradation)
            if driver_laps.empty:
                logger.debug("Empty laps, returning 0.0 rating")
                return 0.0
            
            driver_laps = validator.validate_dataframe(driver_laps, "Driver laps", min_rows=1)
            
            fastest = driver_laps['LapTime'].min()
            avg = driver_laps['LapTime'].mean()
            consistency = (avg / fastest) - 1  # Delta from fastest
            
            # Score: 100 for fastest, decreases with inconsistency
            rating = max(0.0, min(100.0, 100.0 - (consistency * 50.0)))
            logger.debug(f"Performance rating: {rating:.1f}")
            return rating
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Performance rating computation failed: {e}")
            return 0.0


# Singleton
telemetry_service = TelemetryService()
