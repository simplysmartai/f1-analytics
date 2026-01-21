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

# Page configuration
st.set_page_config(
    page_title="F1 Analytics Dashboard | nexairi.com",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #e10600 0%, #ff1801 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #e10600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize FastF1 cache
@st.cache_resource
def setup_cache():
    cache_dir = Path.home() / '.fastf1-cache'
    cache_dir.mkdir(exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    return cache_dir

setup_cache()

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
        options=list(range(current_year, 2017, -1)),
        index=0 if current_year <= 2025 else 1
    )
    
    # Session type
    session_type = st.radio(
        "Session Type",
        options=["Race", "Qualifying", "Practice 1", "Practice 2", "Practice 3", "Sprint", "Sprint Qualifying"],
        index=0
    )
    
    session_map = {
        "Race": "R",
        "Qualifying": "Q",
        "Practice 1": "FP1",
        "Practice 2": "FP2",
        "Practice 3": "FP3",
        "Sprint": "S",
        "Sprint Qualifying": "SQ"
    }
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Built on [F1 Race Replay](https://github.com/IAmTomShaw/f1-race-replay) 
    by Tom Shaw.
    
    Enhanced with AI analytics by **nexairi.com**
    """)

# Load race schedule
@st.cache_data
def load_schedule(year):
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule
    except Exception as e:
        st.error(f"Error loading schedule: {e}")
        return None

schedule = load_schedule(year)

if schedule is not None:
    # Round selection
    with st.sidebar:
        # Filter to only past/current races
        today = pd.Timestamp.now()
        available_races = schedule[schedule['EventDate'] <= today]
        
        if len(available_races) == 0:
            st.warning(f"No races available yet for {year}")
            st.stop()
        
        race_options = {
            f"Round {row['RoundNumber']}: {row['EventName']} ({row['Country']})": row['RoundNumber']
            for _, row in available_races.iterrows()
        }
        
        # REORGANIZED: Grand Prix selector (moved down after Season)
        selected_race = st.selectbox("Grand Prix", options=list(race_options.keys()))
        round_number = race_options[selected_race]

    # Load session data
    @st.cache_data
    def load_session(year, round_num, session_type):
        try:
            with st.spinner(f"Loading {session_type} data..."):
                session = fastf1.get_session(year, round_num, session_type)
                session.load()
                return session
        except Exception as e:
            st.error(f"Error loading session: {e}")
            return None

    session = load_session(year, round_number, session_map[session_type])

    if session is not None:
        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏎️ Driver Analysis", "📈 Telemetry", "🤖 AI Insights"])
        
        with tab1:
            # Overview tab
            col1, col2, col3, col4 = st.columns(4)
            
            event_info = session.event
            
            with col1:
                st.metric("🏁 Event", event_info['EventName'])
            with col2:
                st.metric("📍 Location", event_info['Location'])
            with col3:
                st.metric("📅 Date", event_info['EventDate'].strftime('%Y-%m-%d'))
            with col4:
                st.metric("🔢 Round", event_info['RoundNumber'])
            
            st.markdown("### 🏆 Session Results")
            
            # Get results
            if session_type in ["Race", "Sprint"]:
                results = session.results
                results_df = pd.DataFrame({
                    'Position': results['Position'],
                    'Driver': results['Abbreviation'],
                    'Team': results['TeamName'],
                    'Time': results['Time'],
                    'Status': results['Status'],
                    'Points': results['Points']
                })
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
            elif session_type in ["Qualifying", "Sprint Qualifying"]:
                results = session.results
                results_df = pd.DataFrame({
                    'Position': results['Position'],
                    'Driver': results['Abbreviation'],
                    'Team': results['TeamName'],
                    'Q1': results['Q1'],
                    'Q2': results['Q2'],
                    'Q3': results['Q3']
                })
                st.dataframe(results_df, use_container_width=True, hide_index=True)
        
        with tab2:
            # Driver Analysis tab
            st.markdown("### 🏎️ Compare Drivers")
            
            drivers = session.drivers
            driver_info = {session.get_driver(d)['Abbreviation']: d for d in drivers}
            
            col1, col2 = st.columns(2)
            
            with col1:
                driver1 = st.selectbox("Driver 1", options=list(driver_info.keys()), index=0)
            with col2:
                driver2 = st.selectbox("Driver 2", options=list(driver_info.keys()), index=1 if len(driver_info) > 1 else 0)
            
            if driver1 and driver2:
                # Get driver laps
                driver1_laps = session.laps.pick_driver(driver1)
                driver2_laps = session.laps.pick_driver(driver2)
                
                # Lap time comparison
                st.markdown("#### ⏱️ Lap Time Comparison")
                
                fig = go.Figure()
                
                # Driver 1 lap times
                fig.add_trace(go.Scatter(
                    x=driver1_laps['LapNumber'],
                    y=driver1_laps['LapTime'].dt.total_seconds(),
                    mode='lines+markers',
                    name=driver1,
                    line=dict(width=2)
                ))
                
                # Driver 2 lap times
                fig.add_trace(go.Scatter(
                    x=driver2_laps['LapNumber'],
                    y=driver2_laps['LapTime'].dt.total_seconds(),
                    mode='lines+markers',
                    name=driver2,
                    line=dict(width=2)
                ))
                
                fig.update_layout(
                    xaxis_title="Lap Number",
                    yaxis_title="Lap Time (seconds)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics comparison
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{driver1} Stats**")
                    fastest_lap1 = driver1_laps['LapTime'].min()
                    avg_lap1 = driver1_laps['LapTime'].mean()
                    st.metric("Fastest Lap", str(fastest_lap1).split()[-1] if pd.notna(fastest_lap1) else "N/A")
                    st.metric("Average Lap", str(avg_lap1).split()[-1] if pd.notna(avg_lap1) else "N/A")
                
                with col2:
                    st.markdown(f"**{driver2} Stats**")
                    fastest_lap2 = driver2_laps['LapTime'].min()
                    avg_lap2 = driver2_laps['LapTime'].mean()
                    st.metric("Fastest Lap", str(fastest_lap2).split()[-1] if pd.notna(fastest_lap2) else "N/A")
                    st.metric("Average Lap", str(avg_lap2).split()[-1] if pd.notna(avg_lap2) else "N/A")
        
        with tab3:
            # Telemetry tab
            st.markdown("### 📡 Telemetry Data")
            
            drivers = session.drivers
            driver_info = {session.get_driver(d)['Abbreviation']: d for d in drivers}
            
            selected_driver = st.selectbox("Select Driver", options=list(driver_info.keys()))
            
            if selected_driver:
                driver_laps = session.laps.pick_driver(selected_driver)
                
                # Let user select a lap
                lap_options = driver_laps['LapNumber'].tolist()
                selected_lap_num = st.selectbox("Select Lap", options=lap_options)
                
                if selected_lap_num:
                    lap = driver_laps[driver_laps['LapNumber'] == selected_lap_num].iloc[0]
                    
                    # Get telemetry for the lap
                    try:
                        telemetry = lap.get_telemetry()
                        
                        # Speed trace
                        st.markdown("#### 🏁 Speed Trace")
                        fig_speed = px.line(
                            telemetry, 
                            x='Distance', 
                            y='Speed',
                            title=f"{selected_driver} - Lap {selected_lap_num} Speed"
                        )
                        fig_speed.update_xaxis(title="Distance (m)")
                        fig_speed.update_yaxis(title="Speed (km/h)")
                        st.plotly_chart(fig_speed, use_container_width=True)
                        
                        # Throttle and Brake
                        st.markdown("#### 🎛️ Throttle & Brake")
                        fig_controls = go.Figure()
                        
                        fig_controls.add_trace(go.Scatter(
                            x=telemetry['Distance'],
                            y=telemetry['Throttle'],
                            mode='lines',
                            name='Throttle',
                            fill='tozeroy',
                            line=dict(color='green')
                        ))
                        
                        fig_controls.add_trace(go.Scatter(
                            x=telemetry['Distance'],
                            y=telemetry['Brake'],
                            mode='lines',
                            name='Brake',
                            fill='tozeroy',
                            line=dict(color='red')
                        ))
                        
                        fig_controls.update_xaxis(title="Distance (m)")
                        fig_controls.update_yaxis(title="Input (%)")
                        st.plotly_chart(fig_controls, use_container_width=True)
                        
                        # Gear changes
                        st.markdown("#### ⚙️ Gear Usage")
                        fig_gear = px.line(
                            telemetry,
                            x='Distance',
                            y='nGear',
                            title=f"Gear Selection"
                        )
                        fig_gear.update_yaxis(title="Gear", dtick=1)
                        fig_gear.update_xaxis(title="Distance (m)")
                        st.plotly_chart(fig_gear, use_container_width=True)
                        
                    except Exception as e:
                        st.warning(f"Telemetry data not available for this lap: {e}")
        
        with tab4:
            # AI Insights tab
            st.markdown("### 🤖 AI-Powered Insights")
            
            st.info("🚀 **Coming Soon!** AI-powered race predictions, strategy analysis, and performance insights.")
            
            # Placeholder for future AI features
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Planned Features")
                st.markdown("""
                - **Race Outcome Predictions** - ML models predicting race results
                - **Optimal Strategy Analysis** - AI-suggested pit strategies
                - **Driver Performance Scoring** - Comprehensive driver ratings
                - **Weather Impact Modeling** - Predict how weather affects pace
                - **Natural Language Q&A** - Ask questions about the data
                """)
            
            with col2:
                st.markdown("#### 💡 Example Insights")
                
                # Simple analytics as placeholder
                if session_type in ["Race", "Sprint"]:
                    try:
                        # Fastest lap analysis
                        fastest_laps = session.laps.pick_fastest()
                        fastest_driver = fastest_laps['Driver'].iloc[0]
                        fastest_time = fastest_laps['LapTime'].iloc[0]
                        
                        st.success(f"⚡ **Fastest Lap**: {fastest_driver} - {str(fastest_time).split()[-1]}")
                        
                        # Tire strategy summary
                        st.info(f"📊 **Total Laps**: {session.laps['LapNumber'].max()}")
                        
                    except Exception as e:
                        st.warning("Analysis not available for this session")

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
