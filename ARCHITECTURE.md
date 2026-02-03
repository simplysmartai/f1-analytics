# F1 Analytics Dashboard - Architecture Documentation

## System Architecture Overview

The F1 Analytics Dashboard is built as a **layered, service-oriented architecture** with clear separation of concerns, comprehensive error handling, and production-ready performance monitoring.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    UI Layer (Streamlit)                 │
│  ├─ app.py (main orchestrator, 160 lines)               │
│  └─ ui/pages/ (modular tab components)                  │
│     ├─ overview.py (session info, results)              │
│     ├─ driver_analysis.py (lap comparisons)             │
│     ├─ telemetry.py (speed/throttle/brake traces)       │
│     └─ ai_insights.py (predictions, ratings)            │
├─────────────────────────────────────────────────────────┤
│                  UI Components Layer                    │
│  ├─ ui/components/sidebar.py (race selection)           │
│  ├─ ui/styles.py (centralized CSS)                      │
│  └─ config/settings.py (UI configuration)               │
├─────────────────────────────────────────────────────────┤
│                  Service Layer (Business Logic)         │
│  ├─ services/f1_data_service.py (FastF1 API wrapper)   │
│  ├─ services/telemetry_service.py (data analysis)       │
│  └─ services/ai_service.py (ML predictions)             │
├─────────────────────────────────────────────────────────┤
│               Utilities & Cross-Cutting Concerns        │
│  ├─ utils/logger.py (logging infrastructure)            │
│  ├─ utils/validators.py (input validation)              │
│  ├─ utils/exceptions.py (custom exception hierarchy)    │
│  ├─ utils/decorators.py (error handling, logging)       │
│  ├─ utils/performance.py (performance monitoring)       │
│  └─ utils/caching.py (smart caching with TTL/LRU)      │
├─────────────────────────────────────────────────────────┤
│                   External Services                     │
│  └─ FastF1 (F1 telemetry API)                           │
│  └─ Streamlit (Web framework)                           │
│  └─ Plotly (Visualization)                              │
└─────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Service Pattern
Services encapsulate business logic and are testable pure Python:

```python
# No Streamlit imports in services - testable anywhere
class TelemetryService:
    @staticmethod
    @monitor_performance("create_lap_comparison_chart")
    def create_lap_comparison_chart(driver1_laps, driver2_laps, names):
        # Pure Python business logic
        return figure
```

### 2. Singleton Pattern
Global instances for single responsibility:

```python
# config/settings.py
settings = Settings()

# utils/logger.py
logger = setup_logger()

# utils/performance.py
monitor = PerformanceMonitor()

# utils/caching.py
global_cache = SmartCache()
```

### 3. Decorator Pattern
Cross-cutting concerns applied non-intrusively:

```python
@st.cache_data(ttl=3600)
@monitor_performance("get_schedule")
@validate_inputs
def get_schedule(year: int):
    pass
```

### 4. Repository Pattern
Data service abstracts FastF1 API:

```python
# Services don't interact with FastF1 directly
# All access goes through f1_data_service
schedule = data_service.get_schedule(year)
session = data_service.get_session(year, round, session_type)
```

## Data Flow

### Loading Race Data

```
User selects race in UI
  ↓
app.py calls data_service.get_schedule(year)
  ↓
[Validation] year checked against rules
  ↓
[Caching] Check if schedule cached (TTL 3600s)
  ↓
[Performance Monitor] Start timing
  ↓
FastF1 API: fetch schedule
  ↓
[Validation] Verify DataFrame structure
  ↓
[Performance Monitor] Record duration
  ↓
[Caching] Store result with TTL
  ↓
Return to UI
```

### Rendering Tab Content

```
User clicks tab
  ↓
app.py calls page module render()
  ↓
Page module (e.g., driver_analysis.py)
  ├─ [Validation] Verify session object
  ├─ [Logging] Log operation start
  ├─ Call telemetry_service for data
  ├─ Call ai_service for predictions
  ├─ [Performance Monitor] Track durations
  ├─ [Error Handling] Catch/log exceptions
  └─ Return rendered UI
```

## Error Handling Strategy

### Exception Hierarchy

```
F1DashboardException (base)
├─ DataLoadException (FastF1 API failures)
├─ CacheException (caching issues)
├─ ValidationException (input validation)
├─ SessionDataException (session data problems)
└─ (custom exceptions for specific domains)
```

### Error Handling Flow

```
try:
    # Validate inputs
    validator.validate_year(year)
    
    # Perform operation
    result = external_api_call()
    
    # Validate result
    validator.validate_dataframe(result)
    
    return result

except ValidationException:
    # Input validation failed - re-raise for user feedback
    logger.warning(f"Validation failed: {e}")
    raise

except Exception as e:
    # Unexpected error - log details, raise domain exception
    logger.error(f"Operation failed: {e}")
    raise DataLoadException(f"Cannot load data: {e}") from e
```

## Validation Strategy

### Multi-Layer Validation

1. **Input Validation** (at service entry points)
   ```python
   year = validator.validate_year(year)
   round_num = validator.validate_round_number(round_num)
   session_type = validator.validate_session_type(session_type)
   ```

2. **Data Validation** (after external calls)
   ```python
   schedule = validator.validate_dataframe(schedule, "Schedule")
   validator.validate_session_object(session)
   ```

3. **Column Validation** (for DataFrames)
   ```python
   telemetry = validator.validate_telemetry_columns(
       telemetry, 
       required=['Distance', 'Speed', 'Throttle', 'Brake']
   )
   ```

## Caching Strategy

### Three-Level Caching

1. **Streamlit Cache** (via decorator)
   ```python
   @st.cache_data(ttl=3600)  # Fastest, but Streamlit-specific
   def get_schedule(year):
       pass
   ```

2. **Smart Cache** (application-level)
   ```python
   global_cache.set("key", value, ttl_seconds=3600)
   cached_value = global_cache.get("key")
   ```

3. **Function Decorator** (automatic)
   ```python
   @cached(ttl_seconds=3600)
   def expensive_computation(args):
       pass
   ```

### Cache Hit Rate Optimization

- Schedule: cached for 1 hour (changes rarely)
- Session data: cached for 1 hour (static historical data)
- Telemetry charts: cached by driver/lap (computed once)
- Performance ratings: cached by session (computed once)

## Performance Monitoring

### What Gets Tracked

Every major service operation is monitored:

```
Operation          | Duration Range | Impact
─────────────────────────────────────────────
get_schedule       | 100-500ms      | Critical
get_session        | 200-1000ms     | Critical
get_driver_laps    | 50-200ms       | High
create_lap_chart   | 10-100ms       | Medium
compute_rating     | 1-10ms         | Low
```

### Performance Metrics Collected

- **Duration**: milliseconds per operation
- **Success/Failure**: operation outcome
- **Cache Hits/Misses**: caching effectiveness
- **Error Messages**: for debugging
- **Statistics**: slowest ops, average duration

## Testing Strategy

### Test Coverage

| Layer | Tests | Coverage |
|-------|-------|----------|
| Services | 9 | All major methods |
| Validators | 23 | All validators, edge cases |
| Performance | 19 | Monitoring, caching |
| Integration | 4+ | End-to-end flows |
| **Total** | **55+** | Comprehensive |

### Test Types

1. **Unit Tests** (pure Python, fast)
   - Service methods isolated
   - Validators with edge cases
   - Performance components

2. **Integration Tests** (component interaction)
   - Validation flow through services
   - Caching with performance monitoring
   - Error propagation

3. **Manual Tests** (UI interaction)
   - Race selection workflow
   - Tab rendering
   - Error messages

## Configuration Management

### Centralized Settings

```python
# config/settings.py
class Settings:
    # FastF1 configuration
    FASTF1_SEASON_START = 2018
    CACHE_DIR = Path.home() / ".fastf1-cache"
    CACHE_SCHEDULE_TTL = 3600
    CACHE_SESSION_TTL = 3600
    
    # Streamlit UI
    PAGE_CONFIG = {
        "page_title": "F1 Analytics Dashboard",
        "layout": "wide",
    }
    
    # Session types
    SESSION_TYPES = {
        "Race": "R",
        "Qualifying": "Q",
        ...
    }
```

## Security Considerations

1. **Input Validation**: All external inputs validated
2. **Error Messages**: Don't expose internal details to users
3. **Logging**: All operations logged for audit trail
4. **No Secrets**: Configuration stored safely, no credentials in code

## Scalability Considerations

### Current Limitations & Future Improvements

| Aspect | Current | Future |
|--------|---------|--------|
| **Caching** | In-memory only | Add Redis for multi-process |
| **Data** | Single season | Multi-season support |
| **Users** | Single user (Streamlit) | Add auth/multi-user |
| **Performance** | Monitoring only | Add alerts/thresholds |
| **Storage** | Cache only | Add database |

## Development Workflow

### Adding a New Feature

1. **Create Service Method**
   ```python
   # services/new_service.py
   @monitor_performance("new_operation")
   def new_operation(data):
       validator.validate_dataframe(data)
       # Business logic
       return result
   ```

2. **Write Tests**
   ```python
   # tests/test_new_feature.py
   def test_new_operation_valid_data():
       # Test implementation
   ```

3. **Create UI Component (if needed)**
   ```python
   # ui/pages/new_page.py
   def render(session):
       service.new_operation(session)
   ```

4. **Update Main App**
   ```python
   # app.py - add tab
   with tab_new:
       new_page.render(session)
   ```

## Directory Structure

```
f1-project/
├── app.py                          # Main Streamlit app
├── config/
│   ├── __init__.py
│   └── settings.py                 # Centralized configuration
├── services/
│   ├── __init__.py
│   ├── f1_data_service.py          # FastF1 integration
│   ├── telemetry_service.py        # Data analysis
│   └── ai_service.py               # ML predictions
├── ui/
│   ├── __init__.py
│   ├── styles.py                   # CSS styling
│   ├── components/
│   │   ├── __init__.py
│   │   └── sidebar.py              # Race selection
│   └── pages/
│       ├── __init__.py
│       ├── overview.py             # Overview tab
│       ├── driver_analysis.py      # Driver comparison
│       ├── telemetry.py            # Telemetry visualization
│       └── ai_insights.py          # AI predictions
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Logging setup
│   ├── exceptions.py               # Custom exceptions
│   ├── validators.py               # Input validation
│   ├── decorators.py               # Reusable decorators
│   ├── performance.py              # Performance monitoring
│   └── caching.py                  # Smart caching
└── tests/
    ├── __init__.py
    ├── conftest.py                 # Pytest fixtures
    ├── test_services.py            # Service tests
    ├── test_validation.py          # Validator tests
    └── test_performance.py         # Performance tests
```

## Key Metrics

### Code Quality

| Metric | Value |
|--------|-------|
| Total Lines of Code | ~2,500 |
| Test Coverage | 55+ tests |
| Type Hints | 100% |
| Documentation | Comprehensive |

### Performance

| Operation | Time | Cached |
|-----------|------|--------|
| Load Schedule | 200-300ms | 1 hour |
| Load Session | 500-800ms | 1 hour |
| Generate Chart | 10-50ms | Per session |
| Compute Rating | 1-5ms | Per session |

### Reliability

| Aspect | Status |
|--------|--------|
| Error Handling | ✅ Comprehensive |
| Input Validation | ✅ 100% coverage |
| Logging | ✅ All operations |
| Performance Monitoring | ✅ All services |
| Testing | ✅ Unit + Integration |

## Deployment Checklist

- [ ] All 55+ tests passing
- [ ] Performance monitoring verified
- [ ] Caching working as expected
- [ ] Error handling tested
- [ ] Documentation complete
- [ ] Configuration validated
- [ ] Dependencies installed
- [ ] Cache directory writable
- [ ] FastF1 API accessible
- [ ] Streamlit port available

## Support & Troubleshooting

### Common Issues

1. **Cache Issues**
   - Clear cache: Delete `~/.fastf1-cache`
   - Check permissions: Cache directory must be writable

2. **Performance Issues**
   - Check cache hit rate: `monitor.get_stats()['cache_hit_rate']`
   - Review slowest ops: `monitor.get_slowest_operations()`

3. **Data Loading Issues**
   - Verify FastF1 API accessible
   - Check internet connection
   - Review error logs in console

## References

- [FastF1 Documentation](https://theoehrly.github.io/Fast-F1/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
