"""Application configuration management"""
from pathlib import Path
from typing import Dict, Any
import os

class Settings:
    """Central configuration for the application"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    CACHE_DIR = Path.home() / '.fastf1-cache'
    
    # FastF1 Settings
    FASTF1_ENABLE_CACHE = True
    FASTF1_SEASON_START = 2018
    
    # Streamlit Settings
    PAGE_CONFIG = {
        'page_title': 'F1 Analytics Dashboard | nexairi.com',
        'page_icon': '🏎️',
        'layout': 'wide',
        'initial_sidebar_state': 'expanded'
    }
    
    # UI Settings
    UI_COLORS = {
        'primary_red': '#e10600',
        'primary_red_light': '#ff1801',
        'text_secondary': '#666',
        'background_light': '#f0f2f6'
    }
    
    # Session Types
    SESSION_TYPES = {
        'Race': 'R',
        'Qualifying': 'Q',
        'Practice 1': 'FP1',
        'Practice 2': 'FP2',
        'Practice 3': 'FP3',
        'Sprint': 'S',
        'Sprint Qualifying': 'SQ'
    }
    
    # Cache TTL (in seconds)
    CACHE_SCHEDULE_TTL = 3600  # 1 hour
    CACHE_SESSION_TTL = 7200   # 2 hours
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        cls.CACHE_DIR.mkdir(exist_ok=True)
        return True

# Singleton instance
settings = Settings()
