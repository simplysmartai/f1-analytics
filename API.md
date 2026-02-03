# F1 Analytics Dashboard - API & Module Documentation

## Services API

### F1DataService

Handles all FastF1 data operations.

```python
from services.f1_data_service import data_service

# Get F1 schedule for a given year
schedule: pd.DataFrame = data_service.get_schedule(year=2025)
# Returns: DataFrame with EventName, EventDate, RoundNumber, Country, etc.
# Cached for 1 hour
# Raises: DataLoadException, ValidationException

# Load specific race session
session: Any = data_service.get_session(
    year=2025,
    round_num=1,
    session_type="Race"  # "Race", "Qualifying", "Practice 1-3", "Sprint"
)
# Returns: FastF1 session object with laps, results, telemetry
# Cached for 1 hour
# Raises: DataLoadException, ValidationException

# Extract session results
results: pd.DataFrame = data_service.get_session_results(session)
# Returns: DataFrame with Position, Driver, Team, Time, Status, Points
```

**Error Handling:**
```python
try:
    schedule = data_service.get_schedule(1900)  # Invalid year
except ValidationException as e:
    logger.warning(f"Invalid input: {e}")
except DataLoadException as e:
    logger.error(f"Failed to load data: {e}")
    st.error("Could not load F1 schedule")
```

### TelemetryService

Analyzes driver telemetry and creates visualizations.

```python
from services.telemetry_service import telemetry_service

# Get all laps for a driver
driver_laps: pd.DataFrame = telemetry_service.get_driver_laps(
    session=session,
    driver="VER"  # Driver abbreviation
)
# Returns: DataFrame with LapNumber, LapTime, Compound, etc.

# Create lap time comparison chart
figure: go.Figure = telemetry_service.create_lap_comparison_chart(
    driver1_laps=ver_laps,
    driver2_laps=ham_laps,
    driver1_name="VER",
    driver2_name="HAM"
)
# Returns: Plotly Figure showing lap time progression

# Create speed trace visualization
figure: go.Figure = telemetry_service.create_speed_trace(
    telemetry=lap.get_telemetry(),
    driver="VER",
    lap_num=42
)
# Returns: Plotly Figure with speed vs distance

# Create throttle/brake chart
figure: go.Figure = telemetry_service.create_controls_chart(
    telemetry=lap.get_telemetry()
)
# Returns: Plotly Figure with throttle/brake inputs vs distance

# Compute driver performance rating
rating: float = telemetry_service.compute_performance_rating(
    driver_laps=driver_laps
)
# Returns: Float between 0-100 (higher = better consistency)
# Returns 0.0 if no valid lap times
```

**Performance:**
- All methods decorated with `@monitor_performance()`
- Metrics tracked automatically
- Cache hits recorded

### AIService

Machine learning and analytics.

```python
from services.ai_service import ai_service

# Predict race winner based on qualifying
predictions: Dict[str, float] = ai_service.predict_race_winner(
    quali_data=session.results
)
# Returns: Dict with {"VER": 0.35, "HAM": 0.25, ...}
# Probabilities sum to ~1.0
# Performance factors: grid position, team, historical data

# Compute performance rating (alternative to telemetry service)
rating: float = ai_service.compute_performance_rating(
    driver_laps=driver_laps
)
# Returns: Float 0-100 (consistent with telemetry service)

# Analyze pit strategy (framework for expansion)
strategy: List[Dict] = ai_service.analyze_pit_strategy(
    session=session
)
# Returns: List of strategy recommendations
# Framework ready for future enhancement
```

## Utilities API

### Logger

Centralized logging throughout application.

```python
from utils.logger import logger

logger.debug("Detailed diagnostic information")
logger.info("General information about operation")
logger.warning("Warning about potential issue")
logger.error("Error occurred, operation may have failed")
logger.critical("Critical error, operation cannot continue")

# Output includes: timestamp, level, module, message
# Format: 2025-02-03 16:30:45 - f1-dashboard - INFO - Message
```

### Validators

Input validation and data integrity checks.

```python
from utils.validators import validator
from utils.exceptions import ValidationException

# Year validation
try:
    year = validator.validate_year(2025)
    # 1950 (F1 start) to current year
except ValidationException:
    # Invalid year - handle error

# Round number validation
try:
    round_num = validator.validate_round_number(5)
    # 1 to 24 (typical F1 season)
except ValidationException:
    # Invalid round

# Session type validation
try:
    session_type = validator.validate_session_type("Race")
    # "Race", "Sprint", "Qualifying", "Sprint Qualifying", "Practice"
except ValidationException:
    # Invalid session type

# DataFrame validation
try:
    df = validator.validate_dataframe(schedule, "Schedule", min_rows=1)
    # Must be DataFrame, not empty, >= min_rows
except ValidationException:
    # Invalid DataFrame

# Column validation
try:
    telemetry = validator.validate_telemetry_columns(
        lap.get_telemetry(),
        required=['Distance', 'Speed', 'Throttle', 'Brake']
    )
except ValidationException:
    # Missing required columns

# Driver abbreviation validation
try:
    driver = validator.validate_driver_abbr("VER")
except ValidationException:
    # Invalid driver format

# Session object validation
try:
    validator.validate_session_object(session)
    # Checks for required attributes
except ValidationException:
    # Invalid session object
```

### Performance Monitoring

Track and analyze performance metrics.

```python
from utils.performance import monitor, monitor_performance

# Automatic decoration for any function
@monitor_performance("my_operation")
def expensive_function():
    pass

expensive_function()

# Get global statistics
stats = monitor.get_stats()
# {
#     'total_metrics': 156,
#     'successful': 155,
#     'failed': 1,
#     'cache_hits': 89,
#     'cache_misses': 12,
#     'cache_hit_rate': '88.1%',
#     'avg_duration_ms': '245.34',
#     'slowest_operations': [
#         'PerformanceMetric(operation=get_session, duration_ms=850.23)',
#         ...
#     ]
# }

# Get average duration for specific operation
avg_duration = monitor.get_average_duration("get_session")
# Returns: float (milliseconds)

# Get slowest operations (top N)
slowest = monitor.get_slowest_operations(limit=5)
# Returns: List of PerformanceMetric objects

# Get failed operations
failed = monitor.get_failed_operations()
# Returns: List of PerformanceMetric objects with success=False

# Cache statistics
cache_hit_rate = monitor.get_cache_hit_rate()
# Returns: float (percentage 0-100)

# Clear all metrics
monitor.clear()
```

### Caching

Smart caching with TTL and LRU eviction.

```python
from utils.caching import SmartCache, cached, global_cache

# Using decorator (recommended)
@cached(ttl_seconds=3600)
def expensive_computation(x, y):
    # Function result cached for 1 hour
    # Same arguments -> cached result
    # Different arguments -> new computation
    return x + y

result = expensive_computation(5, 10)  # Computed
result = expensive_computation(5, 10)  # From cache (fast!)

# Manual cache operations
global_cache.set("my_key", "my_value", ttl_seconds=3600)
value = global_cache.get("my_key")  # Returns "my_value" if not expired

# Cache statistics
stats = global_cache.get_stats()
# {
#     'size': 45,
#     'max_size': 500,
#     'hits': 234,
#     'misses': 12,
#     'hit_rate': '95.1%',
#     'total_accesses': 246
# }

# Clear cache
global_cache.clear()

# Create custom cache
my_cache = SmartCache(max_size=100, default_ttl=1800)
my_cache.set("key1", "value1")
value = my_cache.get("key1")
```

## UI Components

### Sidebar Component

Race selection component.

```python
from ui.components.sidebar import SidebarComponent

# In Streamlit app
with st.sidebar:
    result = SidebarComponent.render()
    
    if result:
        year, session_type, round_number = result
        # Use selected values
    else:
        # User interaction ongoing or error
```

### Page Modules

Each tab is a self-contained module.

#### Overview Page

```python
from ui.pages import overview

# Render overview tab
with tab_overview:
    overview.render(session, session_type)
    # Displays: Event info (date, location, round)
    # Displays: Session results (positions, times, points)
```

#### Driver Analysis Page

```python
from ui.pages import driver_analysis

# Render driver analysis tab
with tab_driver_analysis:
    driver_analysis.render(session)
    # Displays: Driver selection dropdowns
    # Displays: Lap time comparison chart
    # Displays: Statistics (fastest, average laps)
```

#### Telemetry Page

```python
from ui.pages import telemetry

# Render telemetry tab
with tab_telemetry:
    telemetry.render(session)
    # Displays: Driver and lap selection
    # Displays: Speed trace chart
    # Displays: Throttle/brake input chart
    # Displays: Gear usage chart
```

#### AI Insights Page

```python
from ui.pages import ai_insights

# Render AI insights tab
with tab_ai_insights:
    ai_insights.render(session)
    # Displays: Race outcome predictions
    # Displays: Performance ratings
    # Displays: Strategy analysis
```

## Configuration API

### Settings

Centralized configuration.

```python
from config.settings import settings

# Validate all settings
settings.validate()

# Access settings
year_range = range(settings.FASTF1_SEASON_START, 2026)
cache_dir = settings.CACHE_DIR
schedule_ttl = settings.CACHE_SCHEDULE_TTL

# Page configuration
page_config = settings.PAGE_CONFIG
# Returns: {"page_title": "...", "layout": "wide", ...}

# Session types mapping
session_types = settings.SESSION_TYPES
# Returns: {"Race": "R", "Qualifying": "Q", ...}

# UI colors
colors = settings.UI_COLORS
# Returns: {"primary": "#FF1801", ...}
```

## Error Handling

### Exception Hierarchy

```python
from utils.exceptions import (
    F1DashboardException,      # Base exception
    DataLoadException,         # FastF1 API issues
    CacheException,           # Caching issues
    ValidationException,      # Input validation
    SessionDataException,     # Session data problems
)

# Catch specific errors
try:
    session = data_service.get_session(year, round, session_type)
except ValidationException as e:
    logger.warning(f"Invalid input: {e}")
    st.warning(f"Please check your input: {e}")
except DataLoadException as e:
    logger.error(f"Data load failed: {e}")
    st.error("Could not load session data")
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    st.error("An unexpected error occurred")
```

## Testing API

### Fixtures

Pytest fixtures for testing.

```python
# tests/conftest.py provides:

@pytest.fixture
def sample_laps_data():
    # Returns: Sample lap times DataFrame
    
@pytest.fixture
def sample_quali_data():
    # Returns: Sample qualifying results
    
@pytest.fixture
def sample_schedule():
    # Returns: Sample F1 schedule DataFrame
```

### Test Patterns

```python
# tests/test_services.py
def test_compute_performance_rating_valid_data(sample_laps_data):
    rating = telemetry_service.compute_performance_rating(sample_laps_data)
    assert 0 <= rating <= 100
    assert rating > 0  # Non-empty data should score > 0

def test_get_driver_laps_validation():
    with pytest.raises(ValidationException):
        telemetry_service.get_driver_laps(None, "INVALID_DRIVER")

# tests/test_validation.py
def test_validate_year_valid():
    year = validator.validate_year(2025)
    assert year == 2025

def test_validate_year_too_old():
    with pytest.raises(ValidationException):
        validator.validate_year(1900)
```

## Example Usage

### Complete Workflow

```python
import streamlit as st
from services.f1_data_service import data_service
from services.telemetry_service import telemetry_service
from services.ai_service import ai_service
from utils.logger import logger
from utils.performance import monitor

# Load schedule
try:
    logger.info("Loading F1 schedule for 2025")
    schedule = data_service.get_schedule(2025)
    logger.info(f"Loaded {len(schedule)} races")
except Exception as e:
    logger.error(f"Failed to load schedule: {e}")
    st.error("Could not load F1 schedule")
    st.stop()

# User selects race
race_name = st.selectbox("Select Race", options=schedule['EventName'])
round_num = schedule[schedule['EventName'] == race_name]['RoundNumber'].iloc[0]

# Load session
try:
    logger.info(f"Loading qualifying for R{round_num}")
    session = data_service.get_session(2025, round_num, "Qualifying")
except Exception as e:
    logger.error(f"Failed to load session: {e}")
    st.error("Could not load session")
    st.stop()

# Analyze data
drivers = [session.get_driver(d)['Abbreviation'] for d in session.drivers]
driver1 = st.selectbox("Driver 1", options=drivers)
driver2 = st.selectbox("Driver 2", options=drivers)

if driver1 and driver2:
    # Get laps
    laps1 = telemetry_service.get_driver_laps(session, driver1)
    laps2 = telemetry_service.get_driver_laps(session, driver2)
    
    # Create visualization
    chart = telemetry_service.create_lap_comparison_chart(
        laps1, laps2, driver1, driver2
    )
    st.plotly_chart(chart)
    
    # Show predictions
    predictions = ai_service.predict_race_winner(session.results)
    st.metric(f"{driver1} Win Probability", f"{predictions[driver1]*100:.1f}%")

# Display performance stats
st.sidebar.metric(
    "Cache Hit Rate",
    f"{monitor.get_cache_hit_rate():.1f}%"
)
```

## Best Practices

1. **Always validate input** before passing to services
2. **Use decorators** for automatic monitoring and caching
3. **Handle exceptions** specifically, not broadly
4. **Log operations** at appropriate levels
5. **Test edge cases** and error conditions
6. **Monitor performance** in production
7. **Cache aggressively** for external API calls
8. **Clear cache** only when data changes

## Common Pitfalls

❌ **DON'T:**
```python
# Don't ignore validation errors
schedule = data_service.get_schedule(year)  # Could fail

# Don't catch broad exceptions
try:
    result = service.get_data()
except Exception:
    pass  # Silent failures are bad

# Don't call external APIs repeatedly
for driver in drivers:
    laps = telemetry_service.get_driver_laps(session, driver)
```

✅ **DO:**
```python
# Validate and handle errors specifically
try:
    schedule = data_service.get_schedule(year)
except ValidationException as e:
    logger.warning(f"Invalid year: {e}")
    st.warning("Please select a valid year")
except DataLoadException as e:
    logger.error(f"Data load failed: {e}")
    st.error("Could not load schedule")

# Cache results
@cached(ttl_seconds=3600)
def load_driver_laps(session, driver):
    return telemetry_service.get_driver_laps(session, driver)

# Use cached version
for driver in drivers:
    laps = load_driver_laps(session, driver)  # Cached!
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-02-03 | Initial release with all 5 phases |

## Support

For issues, questions, or contributions:
- Check ARCHITECTURE.md for design details
- Check DEPLOYMENT.md for setup help
- Review test files for usage examples
- Check logs for error details
