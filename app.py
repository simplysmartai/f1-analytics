"""
F1 Analytics Dashboard - Web Application
Built on top of Tom Shaw's F1 Race Replay project
https://github.com/IAmTomShaw/f1-race-replay

Enhanced with AI-powered analytics for nexairi.com
"""

import streamlit as st
import fastf1
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import new modules
from config.settings import settings
from utils.logger import logger
from ui.styles import get_custom_css
from services.f1_data_service import data_service
from ui.components.sidebar import SidebarComponent
from ui.pages import overview, driver_analysis, telemetry, ai_insights

# Initialize configuration and logging
try:
    settings.validate()
    logger.info("F1 Dashboard starting...")
except Exception as e:
    print(f"CRITICAL: Configuration validation failed: {e}")
    import traceback
    traceback.print_exc()

# Page configuration (use settings)
try:
    st.set_page_config(**settings.PAGE_CONFIG)
except Exception as e:
    logger.error(f"Page config error: {e}")

# Custom CSS for branding (use centralized styles)
try:
    st.markdown(get_custom_css(), unsafe_allow_html=True)
except Exception as e:
    logger.error(f"CSS error: {e}")
    st.warning("CSS styling failed - continuing without styles")

# Initialize FastF1 cache (done by service)
try:
    logger.info("Initializing FastF1 cache...")
    # Cache is initialized by data_service on import
    logger.info("FastF1 cache initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize cache: {e}")
    logger.warning("Continuing without cache...")

# Header
st.markdown('<h1 class="main-header">🏎️ F1 Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by AI • Built for nexairi.com</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Race Selection
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/F1.svg/1200px-F1.svg.png", width=150)
    st.markdown("## 🏁 Select Race")
    
    # Year selection
    current_year = datetime.now().year
    year = st.selectbox(
        "Season",
        options=list(range(current_year, settings.FASTF1_SEASON_START - 1, -1)),
        index=0 if current_year <= 2025 else 1
    )
    
    # Session type (use from settings)
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

# Load race schedule using service
try:
    logger.info(f"Loading F1 schedule for {year}")
    schedule = data_service.get_schedule(year)
except Exception as e:
    logger.error(f"Failed to load schedule: {e}")
    st.error(f"Could not load F1 schedule: {e}")
    st.stop()

if schedule is not None:
    # Round selection
    with st.sidebar:
        # Filter to only past/current races
        today = pd.Timestamp.now()
        available_races = schedule[schedule['EventDate'] <= today]
        
        if len(available_races) == 0:
            logger.warning(f"No races available yet for {year}")
            st.warning(f"No races available yet for {year}")
            st.stop()
        
        race_options = {
            f"Round {int(row['RoundNumber'])}: {row['EventName']} ({row['Country']})": int(row['RoundNumber'])
            for _, row in available_races.iterrows()
            if int(row['RoundNumber']) > 0 and int(row['RoundNumber']) <= 24
        }
        
        # REORGANIZED: Grand Prix selector (moved down after Season)
        selected_race = st.selectbox("Grand Prix", options=list(race_options.keys()))
        round_number = race_options[selected_race]

    # Load session data using service
    try:
        with st.spinner(f"Loading {session_type} data..."):
            logger.info(f"Loading {session_type} session for R{round_number}/{year}")
            session = data_service.get_session(year, int(round_number), settings.SESSION_TYPES[session_type])
            logger.info(f"Session loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        st.error(f"Error loading session: {e}")
        st.stop()

    if session is not None:
        # Main content area with modular page components
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏎️ Driver Analysis", "📈 Telemetry", "🤖 AI Insights"])
        
        with tab1:
            overview.render(session, session_type)
        
        with tab2:
            driver_analysis.render(session)
        
        with tab3:
            telemetry.render(session)
        
        with tab4:
            ai_insights.render(session)

else:
    st.error("Unable to load F1 schedule. Please try again later.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for <strong>nexairi.com</strong> | Based on <a href='https://github.com/IAmTomShaw/f1-race-replay' target='_blank'>F1 Race Replay</a> by Tom Shaw</p>
    <p>Data provided by FastF1 • No copyright infringement intended</p>
</div>
""", unsafe_allow_html=True)
