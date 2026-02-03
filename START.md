# Getting Started with F1 Analytics Dashboard

## Quick Start (60 seconds)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

**That's it!** 🎉 Your dashboard opens at `http://localhost:3000`

---

## What to Expect

### First Load
- Takes ~5-30 seconds to load initial data (FastF1 API call)
- Subsequent loads are instant thanks to caching
- All data is cached locally at `~/.fastf1-cache/`

### Navigation
1. **Sidebar** - Select Season, Session Type, and Grand Prix
2. **Main Content** - Four tabs:
   - 📊 **Overview** - Event info and session results
   - 🏎️ **Driver Analysis** - Compare drivers lap-by-lap
   - 📈 **Telemetry** - Speed, throttle, brake, gear visualizations
   - 🤖 **AI Insights** - Performance ratings and predictions

### Features
- ✅ Browse all F1 races from 2018-present
- ✅ Interactive Plotly charts
- ✅ Real-time filtering and updates
- ✅ Professional AI-powered analytics

---

## System Requirements

- **Python**: 3.13+ 
- **RAM**: 2GB minimum (4GB recommended)
- **Internet**: Required for FastF1 API calls
- **Storage**: ~500MB for cache (auto-managed)

---

## Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "No races available"
**Solution:** Try a different year or check internet connection
- The app only shows past/completed races
- Current year may have no completed races early in season

### Issue: "Slow performance"
**Solution:** Cache is building. Subsequent loads are fast.
- First load: ~30 seconds
- Subsequent loads: <1 second (cached)

### Issue: "SSL Certificate Error"
**Solution:** Update certificates
```bash
pip install --upgrade certifi
```

---

## Performance Tips

1. **Select recent seasons** - Faster to load
2. **Use same race twice** - Loads instantly from cache
3. **Check browser console** - May show additional details if issues

---

## Advanced Usage

### Check Performance Stats
```python
from utils.performance import monitor
stats = monitor.get_stats()
print(f"Cache hit rate: {stats['cache_hit_rate']}%")
print(f"Avg operation time: {stats['avg_duration_ms']}ms")
```

### Run Tests
```bash
pytest tests/ -v
```

### View Logs
Logs are printed to console and stored at: `logs/f1-dashboard.log`

---

## Architecture

```
Streamlit UI (streamlit run app.py)
    ↓
Service Layer (Pure Python, no Streamlit)
    ├── f1_data_service.py (FastF1 integration)
    ├── telemetry_service.py (Analysis)
    └── ai_service.py (Predictions)
    ↓
Utilities (Logging, Validation, Caching, Performance)
    ↓
FastF1 API (Formula 1 data)
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and features |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design and patterns |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |
| [API.md](API.md) | Complete API reference |
| [START.md](START.md) | This file - Quick start guide |

---

## Next Steps

1. **Run the app** - `streamlit run app.py`
2. **Explore data** - Browse different seasons and races
3. **Read docs** - Check [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
4. **Deploy** - See [DEPLOYMENT.md](DEPLOYMENT.md) for Streamlit Cloud, Docker, etc.

---

## Support

- 📖 See [README.md](README.md) for features
- 🏗️ See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- 🚀 See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- 📊 See [API.md](API.md) for module documentation

---

**Built with ❤️ for nexairi.com** 🏎️

Powered by [FastF1](https://theoehrly.github.io/Fast-F1/) + [Streamlit](https://streamlit.io/)
