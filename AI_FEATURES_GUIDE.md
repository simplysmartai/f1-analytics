# AI Features Implementation Guide

This document outlines how to add AI-powered features to your F1 Analytics Dashboard.

## Phase 1: Simple ML Predictions (Start Here)

### 1. Race Winner Prediction
Use historical data to predict race winners based on qualifying performance.

```python
# Add to requirements.txt:
# scikit-learn>=1.3.0

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def predict_race_winner(quali_results, historical_data):
    """
    Predict race winner based on qualifying results
    Features: quali_position, team, track_type, weather
    """
    # Feature engineering
    features = []
    for driver in quali_results:
        features.append([
            driver['quali_position'],
            driver['team_encoded'],
            driver['track_type'],
            driver['weather_condition']
        ])
    
    # Load pre-trained model or train on historical data
    model = RandomForestClassifier(n_estimators=100)
    # model.fit(X_train, y_train)  # Train on historical data
    
    predictions = model.predict_proba(features)
    return predictions
```

### 2. Lap Time Prediction
Predict lap times based on tire age, fuel load, and track conditions.

```python
from sklearn.linear_model import LinearRegression

def predict_lap_time(lap_number, tire_age, fuel_load, weather):
    """
    Predict lap time for given conditions
    """
    model = LinearRegression()
    
    features = np.array([[lap_number, tire_age, fuel_load, weather]])
    predicted_time = model.predict(features)
    
    return predicted_time
```

### 3. Tire Degradation Model
Calculate tire degradation rate and predict optimal pit stop timing.

```python
def analyze_tire_degradation(lap_times, tire_compound):
    """
    Analyze tire degradation from lap time data
    Returns: degradation_rate, optimal_pit_lap
    """
    # Calculate lap time increase over stint
    time_delta = []
    for i in range(1, len(lap_times)):
        delta = (lap_times[i] - lap_times[i-1]).total_seconds()
        time_delta.append(delta)
    
    # Linear regression to find degradation rate
    degradation_rate = np.mean(time_delta)
    
    # Optimal pit stop when degradation exceeds threshold
    threshold = 0.5  # seconds per lap
    optimal_pit_lap = len([d for d in time_delta if d < threshold])
    
    return {
        'degradation_rate': degradation_rate,
        'optimal_pit_lap': optimal_pit_lap,
        'compound': tire_compound
    }
```

## Phase 2: Advanced ML Models

### 4. Strategy Optimization
Use reinforcement learning or Monte Carlo simulation for pit strategy.

```python
import random

def simulate_race_strategies(current_lap, laps_remaining, tire_age, competitors):
    """
    Monte Carlo simulation for optimal pit strategy
    """
    strategies = []
    num_simulations = 1000
    
    for _ in range(num_simulations):
        # Simulate different pit stop timings
        pit_lap = random.randint(current_lap + 5, current_lap + laps_remaining - 10)
        
        # Calculate expected race time
        race_time = calculate_race_time(
            current_lap, pit_lap, laps_remaining, tire_age
        )
        
        strategies.append({
            'pit_lap': pit_lap,
            'expected_time': race_time,
            'probability_win': calculate_win_probability(race_time, competitors)
        })
    
    # Return best strategy
    return max(strategies, key=lambda x: x['probability_win'])
```

### 5. Driver Performance Rating
Create a comprehensive driver rating system.

```python
def calculate_driver_rating(session_data):
    """
    Multi-factor driver rating algorithm
    Factors: pace, consistency, overtakes, defending, mistakes
    """
    rating = {
        'pace_score': 0,
        'consistency_score': 0,
        'racecraft_score': 0,
        'overall_rating': 0
    }
    
    # Pace: Based on average gap to teammate
    teammate_gap = calculate_teammate_gap(session_data)
    rating['pace_score'] = 100 - (teammate_gap * 10)
    
    # Consistency: Standard deviation of lap times
    lap_times = session_data['LapTime'].dt.total_seconds()
    std_dev = np.std(lap_times)
    rating['consistency_score'] = 100 - (std_dev * 20)
    
    # Racecraft: Position changes, overtakes, defense
    position_gain = calculate_position_changes(session_data)
    rating['racecraft_score'] = 50 + (position_gain * 5)
    
    # Overall weighted rating
    rating['overall_rating'] = (
        rating['pace_score'] * 0.4 +
        rating['consistency_score'] * 0.3 +
        rating['racecraft_score'] * 0.3
    )
    
    return rating
```

## Phase 3: Natural Language AI

### 6. Integration with Claude/GPT for Q&A
Allow users to ask questions about race data in plain English.

```python
import anthropic

def answer_race_question(question, session_data):
    """
    Use Claude API to answer questions about race data
    """
    client = anthropic.Anthropic(api_key="your-api-key")
    
    # Prepare context from race data
    context = f"""
    Race: {session_data.event['EventName']}
    Date: {session_data.event['EventDate']}
    
    Results:
    {session_data.results.to_string()}
    
    Fastest Lap: {session_data.laps.pick_fastest()['Driver'].iloc[0]}
    
    User Question: {question}
    """
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": context}
        ]
    )
    
    return message.content[0].text
```

### Example Integration in Streamlit:
```python
# Add to AI Insights tab:
st.markdown("#### 💬 Ask About This Race")
user_question = st.text_input("What would you like to know?")

if user_question:
    with st.spinner("Analyzing..."):
        answer = answer_race_question(user_question, session)
        st.markdown(answer)
```

## Phase 4: Real-Time Predictions

### 7. Live Race Probability Updates
During live races, update win probabilities in real-time.

```python
import time

def live_race_monitor(year, round_number):
    """
    Monitor live race and update predictions
    """
    while True:
        # Get latest session data
        session = fastf1.get_session(year, round_number, 'R')
        session.load(laps=True, telemetry=False)
        
        # Calculate current probabilities
        current_standings = session.laps.groupby('Driver').last()
        probabilities = calculate_win_probabilities(current_standings)
        
        # Update dashboard
        yield probabilities
        
        # Wait before next update
        time.sleep(10)  # Update every 10 seconds
```

## Phase 5: Computer Vision (Advanced)

### 8. Analyze Race Footage
Use computer vision to extract insights from race videos.

```python
import cv2

def analyze_race_video(video_path):
    """
    Extract insights from race footage
    - Detect overtakes
    - Identify incidents
    - Track car positions
    """
    cap = cv2.VideoCapture(video_path)
    
    insights = {
        'overtakes': [],
        'incidents': [],
        'battle_moments': []
    }
    
    # Process frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Use object detection model to identify cars
        # Track positions and detect overtakes
        # Identify unusual events (crashes, spins)
        
    return insights
```

## Integration Tips

### Adding AI Features to the Streamlit App

1. **Create a new file**: `ai_features.py`
```python
# ai_features.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class F1AIAnalyzer:
    def __init__(self):
        self.models = {}
    
    def predict_winner(self, session):
        # Implementation here
        pass
    
    def analyze_strategy(self, session):
        # Implementation here
        pass
    
    def rate_driver(self, driver_data):
        # Implementation here
        pass
```

2. **Import in app.py**:
```python
from ai_features import F1AIAnalyzer

ai_analyzer = F1AIAnalyzer()
```

3. **Add to AI Insights tab**:
```python
with tab4:
    st.markdown("### 🤖 AI-Powered Insights")
    
    # Race Winner Prediction
    if st.button("Predict Race Winner"):
        with st.spinner("Analyzing..."):
            prediction = ai_analyzer.predict_winner(session)
            st.success(f"Predicted Winner: {prediction['driver']}")
            st.metric("Confidence", f"{prediction['confidence']:.1%}")
    
    # Strategy Analysis
    st.markdown("#### 🎯 Optimal Strategy")
    strategy = ai_analyzer.analyze_strategy(session)
    st.plotly_chart(strategy['visualization'])
```

## Data Sources for Training

1. **Historical Race Data**: Use FastF1 to download 5+ years of data
2. **Weather Data**: Integrate with weather APIs
3. **Track Characteristics**: Create database of track types
4. **Driver Stats**: Build database of driver performance metrics

## Quick Wins (Implement First)

1. ✅ **Fastest Lap Prediction**: Simple linear regression
2. ✅ **Tire Strategy Analyzer**: Basic degradation calculation
3. ✅ **Driver Comparison Scores**: Statistical analysis
4. ✅ **Weather Impact**: Correlate weather with lap times

## Advanced Features (Later)

1. 🎯 Deep Learning models for race outcome prediction
2. 🎯 Neural networks for tire strategy optimization
3. 🎯 NLP for race commentary generation
4. 🎯 Computer vision for video analysis

## Next Steps

1. Start with Phase 1 features (they're the easiest)
2. Test with historical races (2023, 2024 data)
3. Validate predictions against actual results
4. Gradually add more sophisticated models
5. Always cite sources and show confidence levels

---

**Remember**: Start simple, validate, then enhance. Don't try to build everything at once!
