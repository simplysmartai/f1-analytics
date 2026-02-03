"""AI and ML predictions service"""
import pandas as pd
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.performance import monitor_performance


class AIService:
    """AI-powered analytics and predictions"""
    
    @staticmethod
    @monitor_performance("predict_race_winner")
    def predict_race_winner(quali_data: pd.DataFrame) -> Dict[str, float]:
        """
        Predict race winner based on qualifying results.
        
        Args:
            quali_data: DataFrame with qualifying results
            
        Returns:
            Dictionary with driver predictions (name -> probability)
        """
        try:
            logger.info("Computing race winner prediction")
            
            if quali_data.empty:
                logger.warning("Empty quali data for prediction")
                return {}
            
            # Weight based on quali position (simple model)
            predictions = {}
            for idx, row in quali_data.iterrows():
                if 'Position' in row and 'Abbreviation' in row:
                    score = 1.0 / (row['Position'] + 1)
                    predictions[row['Abbreviation']] = score
            
            # Normalize probabilities
            total = sum(predictions.values())
            if total > 0:
                normalized = {k: v/total for k, v in predictions.items()}
                logger.info(f"Generated predictions for {len(normalized)} drivers")
                return normalized
            
            return {}
            
        except Exception as e:
            logger.error(f"Race winner prediction failed: {e}")
            return {}
    
    @staticmethod
    @monitor_performance("compute_performance_rating")
    def compute_performance_rating(driver_laps: pd.DataFrame) -> float:
        """
        Compute driver performance rating (0-100).
        
        Args:
            driver_laps: DataFrame with lap times
            
        Returns:
            Performance rating from 0 to 100
        """
        try:
            if driver_laps.empty:
                logger.debug("Empty laps data for rating")
                return 0.0
            
            # Get lap times
            if 'LapTime' not in driver_laps.columns:
                logger.warning("LapTime column not found")
                return 0.0
            
            # Filter valid lap times
            valid_laps = driver_laps[driver_laps['LapTime'].notna()]
            
            if valid_laps.empty:
                logger.warning("No valid lap times")
                return 0.0
            
            fastest = valid_laps['LapTime'].min()
            avg = valid_laps['LapTime'].mean()
            
            # Delta from fastest lap (as percentage)
            if fastest.total_seconds() > 0:
                consistency = (avg.total_seconds() / fastest.total_seconds()) - 1
                # Score: 100 for perfect, decreases with inconsistency
                rating = max(0.0, 100.0 - (consistency * 50.0))
            else:
                rating = 0.0
            
            logger.info(f"Performance rating: {rating:.1f}")
            return rating
            
        except Exception as e:
            logger.error(f"Performance rating computation failed: {e}")
            return 0.0
    
    @staticmethod
    @monitor_performance("analyze_pit_strategy")
    def analyze_pit_strategy(session: Any) -> List[Dict[str, Any]]:
        """
        Analyze optimal pit strategies.
        
        Args:
            session: FastF1 session object
            
        Returns:
            List of strategy recommendations
        """
        try:
            logger.info("Analyzing pit strategies")
            # TODO: Implement full pit strategy analyzer
            return []
        except Exception as e:
            logger.error(f"Pit strategy analysis failed: {e}")
            return []


# Singleton instance
ai_service = AIService()
