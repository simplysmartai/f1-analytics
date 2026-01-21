"""
F1 AI Features Module - Simple implementations to get started

Add these to your app.py to enable basic AI predictions!
"""

import pandas as pd
import numpy as np
from datetime import timedelta

class SimpleF1AI:
    """
    Basic F1 AI predictions - no complex ML libraries needed!
    These are statistical models that work well for getting started.
    """
    
    @staticmethod
    def predict_race_winner(qualifying_results):
        """
        Predict race winner based on qualifying position and historical data.
        
        Simple rule: 
        - Pole position wins ~40% of the time
        - Top 3 qualifiers win ~75% of the time
        """
        predictions = []
        
        for idx, driver in qualifying_results.iterrows():
            position = driver['Position']
            
            # Calculate win probability based on quali position
            if position == 1:
                probability = 0.40
            elif position == 2:
                probability = 0.25
            elif position == 3:
                probability = 0.15
            elif position <= 5:
                probability = 0.10
            elif position <= 10:
                probability = 0.05
            else:
                probability = 0.02
            
            predictions.append({
                'Driver': driver['Abbreviation'],
                'Team': driver['TeamName'],
                'Quali_Position': position,
                'Win_Probability': probability,
                'Confidence': 'High' if probability > 0.2 else 'Medium' if probability > 0.1 else 'Low'
            })
        
        # Sort by probability
        predictions = sorted(predictions, key=lambda x: x['Win_Probability'], reverse=True)
        
        return pd.DataFrame(predictions)
    
    @staticmethod
    def analyze_tire_strategy(lap_data, driver):
        """
        Analyze tire degradation and suggest optimal pit stop timing.
        """
        driver_laps = lap_data[lap_data['Driver'] == driver].copy()
        
        if len(driver_laps) == 0:
            return None
        
        # Calculate lap time degradation
        driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
        
        # Group by tire compound/stint
        results = []
        
        for compound in driver_laps['Compound'].unique():
            compound_laps = driver_laps[driver_laps['Compound'] == compound]
            
            if len(compound_laps) < 3:
                continue
            
            # Calculate degradation rate (seconds per lap)
            lap_times = compound_laps['LapTimeSeconds'].values
            degradation = np.diff(lap_times).mean()
            
            # Predict optimal stint length
            # Assumption: pit when degradation > 0.3 seconds per lap
            optimal_laps = len(compound_laps) if degradation < 0.3 else int(len(compound_laps) * 0.8)
            
            results.append({
                'Compound': compound,
                'Laps_Run': len(compound_laps),
                'Avg_Degradation': f"{degradation:.3f} sec/lap",
                'Optimal_Stint': f"{optimal_laps} laps",
                'Status': 'Good' if degradation < 0.2 else 'Monitor' if degradation < 0.4 else 'Critical'
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def rate_driver_performance(driver_laps, teammate_laps=None):
        """
        Calculate driver performance rating based on:
        - Pace (lap times)
        - Consistency (standard deviation)
        - Race craft (position changes)
        """
        if len(driver_laps) == 0:
            return None
        
        # Calculate metrics
        lap_times = driver_laps['LapTime'].dt.total_seconds()
        
        # Pace score (normalized to 100)
        median_time = lap_times.median()
        fastest_time = lap_times.min()
        pace_score = (fastest_time / median_time) * 100
        
        # Consistency score (lower std dev = better)
        std_dev = lap_times.std()
        consistency_score = max(0, 100 - (std_dev * 10))
        
        # Position change score
        if 'Position' in driver_laps.columns:
            start_pos = driver_laps.iloc[0]['Position']
            end_pos = driver_laps.iloc[-1]['Position']
            position_gain = start_pos - end_pos
            racecraft_score = 50 + (position_gain * 5)
        else:
            racecraft_score = 50
        
        # Overall rating (weighted average)
        overall = (pace_score * 0.4) + (consistency_score * 0.3) + (racecraft_score * 0.3)
        
        rating = {
            'Pace_Score': round(pace_score, 1),
            'Consistency_Score': round(consistency_score, 1),
            'Racecraft_Score': round(racecraft_score, 1),
            'Overall_Rating': round(overall, 1),
            'Grade': 'A+' if overall > 95 else 'A' if overall > 90 else 'B' if overall > 80 else 'C'
        }
        
        # Add teammate comparison if available
        if teammate_laps is not None and len(teammate_laps) > 0:
            teammate_median = teammate_laps['LapTime'].dt.total_seconds().median()
            gap_to_teammate = ((median_time - teammate_median) / teammate_median) * 100
            rating['Gap_to_Teammate'] = f"{gap_to_teammate:+.2f}%"
        
        return rating
    
    @staticmethod
    def predict_next_lap_time(recent_laps, tire_age, fuel_effect=True):
        """
        Predict next lap time based on recent performance and tire age.
        
        Simple linear model: time increases with tire age and decreases with fuel burn
        """
        if len(recent_laps) < 3:
            return None
        
        # Get recent lap times
        lap_times = recent_laps['LapTime'].dt.total_seconds().values[-5:]
        
        # Calculate trend
        trend = np.mean(np.diff(lap_times))
        
        # Base prediction on last lap + trend
        last_lap = lap_times[-1]
        next_lap_pred = last_lap + trend
        
        # Adjust for tire age (degradation)
        tire_deg_effect = tire_age * 0.02  # 0.02 seconds per lap of tire age
        
        # Adjust for fuel (gets faster as fuel burns)
        fuel_effect_val = -0.01 if fuel_effect else 0  # 0.01 seconds faster per lap
        
        final_prediction = next_lap_pred + tire_deg_effect + fuel_effect_val
        
        return {
            'Predicted_Time': final_prediction,
            'Confidence_Range': (final_prediction - 0.5, final_prediction + 0.5),
            'Factors': {
                'Trend': f"{trend:+.3f}s",
                'Tire_Effect': f"{tire_deg_effect:+.3f}s",
                'Fuel_Effect': f"{fuel_effect_val:+.3f}s"
            }
        }


# ============================================
# HOW TO USE IN YOUR STREAMLIT APP
# ============================================

"""
Add this to your app.py in the AI Insights tab:

from ai_simple import SimpleF1AI

ai = SimpleF1AI()

with tab4:  # AI Insights tab
    st.markdown("### 🤖 AI-Powered Predictions")
    
    # Race Winner Prediction
    if session_type in ["Qualifying", "Sprint Qualifying"]:
        st.markdown("#### 🏆 Race Winner Prediction")
        
        if st.button("Generate Prediction"):
            with st.spinner("Analyzing qualifying data..."):
                predictions = ai.predict_race_winner(session.results)
                
                # Show top 5 predictions
                st.dataframe(
                    predictions.head(5),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Visualization
                fig = px.bar(
                    predictions.head(10),
                    x='Driver',
                    y='Win_Probability',
                    color='Confidence',
                    title="Win Probability by Driver"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Tire Strategy Analysis
    if session_type in ["Race", "Sprint"]:
        st.markdown("#### 🛞 Tire Strategy Analysis")
        
        selected_driver = st.selectbox("Select Driver for Analysis", 
                                      options=session.drivers)
        driver_abbr = session.get_driver(selected_driver)['Abbreviation']
        
        if st.button("Analyze Tire Strategy"):
            with st.spinner("Analyzing tire data..."):
                tire_analysis = ai.analyze_tire_strategy(
                    session.laps, 
                    driver_abbr
                )
                
                if tire_analysis is not None:
                    st.dataframe(tire_analysis, use_container_width=True)
                else:
                    st.warning("Not enough data for analysis")
    
    # Driver Performance Rating
    st.markdown("#### ⭐ Driver Performance Rating")
    
    driver_to_rate = st.selectbox("Rate Driver Performance", 
                                   options=session.drivers,
                                   key="rating_driver")
    driver_abbr = session.get_driver(driver_to_rate)['Abbreviation']
    
    if st.button("Calculate Rating"):
        with st.spinner("Calculating performance rating..."):
            driver_laps = session.laps.pick_driver(driver_abbr)
            rating = ai.rate_driver_performance(driver_laps)
            
            if rating:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Pace Score", rating['Pace_Score'])
                with col2:
                    st.metric("Consistency", rating['Consistency_Score'])
                with col3:
                    st.metric("Racecraft", rating['Racecraft_Score'])
                with col4:
                    st.metric("Overall Grade", rating['Grade'])
                
                st.success(f"Overall Rating: {rating['Overall_Rating']}/100")
"""
