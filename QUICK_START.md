# 🏎️ F1 Analytics Dashboard - Quick Start Guide

## What You Just Got

A complete, working F1 analytics web application ready to run on your computer or deploy to nexairi.com!

## 📁 Files Included

```
f1-analytics-app/
├── 📱 app.py                    # Main Streamlit application (ready to run!)
├── 📋 requirements.txt          # All dependencies
├── 📖 README.md                 # Full documentation
├── 🚀 AI_FEATURES_GUIDE.md      # How to add AI capabilities
├── 🔧 setup.sh / setup.bat      # Easy setup scripts
├── ▶️  run.sh / run.bat          # Launch the app
├── .gitignore                   # Git configuration
└── .streamlit/config.toml       # Streamlit settings
```

## ⚡ 3 Ways to Get Started

### Option 1: Fastest (Mac/Linux)
```bash
cd f1-analytics-app
./setup.sh      # Install everything
./run.sh        # Launch the app!
```

### Option 2: Fastest (Windows)
```cmd
cd f1-analytics-app
setup.bat       # Install everything
run.bat         # Launch the app!
```

### Option 3: Manual
```bash
cd f1-analytics-app
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

## 🎯 What It Does Right Now

### ✅ Working Features
- Browse ALL F1 races from 2018-2025
- View Race, Qualifying, Practice, Sprint sessions
- See official results and standings
- Compare any two drivers lap-by-lap
- Visualize telemetry data:
  - Speed traces
  - Throttle & brake inputs
  - Gear usage
- Interactive charts (zoom, pan, download)
- Responsive design (works on mobile too!)

### 🎨 Branding
- Custom nexairi.com branding
- F1-themed red color scheme
- Professional layout

## 🚀 Next Steps: Adding AI

Check out `AI_FEATURES_GUIDE.md` for:
- Race winner predictions
- Tire strategy optimization  
- Driver performance ratings
- Natural language Q&A (with Claude API)
- Live race probability updates

**Start Simple**: Begin with the "Quick Wins" section - they're easy to implement!

## 🌐 Deploy to the Web

### Deploy to Streamlit Cloud (FREE & EASY)
1. Create a GitHub account if you don't have one
2. Create a new repository
3. Upload these files
4. Go to [share.streamlit.io](https://share.streamlit.io)
5. Connect your repo
6. Click Deploy!

Your app will be live at: `https://your-username-f1-analytics.streamlit.app`

### Deploy to Vercel (Also Free)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Deploy to Your Own Server
The app can run on any server with Python 3.11+:
- AWS EC2
- Google Cloud
- DigitalOcean
- Your own hosting

## 💡 How to Customize

### Change Colors/Branding
Edit the CSS in `app.py` (line ~30):
```python
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #YOUR_COLOR 0%, #YOUR_COLOR 100%);
    }
    </style>
""", unsafe_allow_html=True)
```

### Add Your Logo
Replace line ~60:
```python
st.image("https://YOUR-LOGO-URL.png", width=150)
```

### Change Footer
Edit line ~450+ to add your info

## 📊 Example Use Cases

1. **Race Analysis**: "How did Hamilton perform in Monaco 2024?"
2. **Driver Comparison**: "Who was faster in Brazil - Verstappen or Leclerc?"
3. **Telemetry Study**: "Where exactly did Verstappen lose time?"
4. **Strategy Review**: "Which tire strategy worked best?"

## 🔥 Pro Tips

1. **First Load is Slow**: FastF1 downloads data - this is normal!
2. **Use 2024 Data**: Most complete and recent
3. **Cache Speeds Up**: Second time loading is much faster
4. **Mobile Works**: Access from your phone!

## 🆘 Troubleshooting

**App won't start?**
- Make sure Python 3.11+ is installed
- Try: `pip install --upgrade streamlit`

**No data loading?**
- Check internet connection
- Try a different race/year
- Clear cache: Delete `~/.fastf1-cache/`

**Slow performance?**
- Normal for first load
- Close other apps
- Try a smaller dataset (Practice vs Race)

## 📈 Roadmap

What to add next (in order of difficulty):

1. ✅ **Easy**: Add more stats to Overview tab
2. ✅ **Easy**: Create downloadable reports
3. 🔶 **Medium**: Add ML lap time predictions
4. 🔶 **Medium**: Build tire strategy calculator
5. 🔴 **Hard**: Real-time live race tracking
6. 🔴 **Hard**: Computer vision race analysis

## 🎓 Learning Resources

- **FastF1 Docs**: https://docs.fastf1.dev/
- **Streamlit Docs**: https://docs.streamlit.io/
- **F1 Data Analysis**: https://medium.com/towards-formula-1-analysis
- **Original Project**: https://github.com/IAmTomShaw/f1-race-replay

## 📞 Support

Built with ❤️ for nexairi.com

Need help? The FastF1 and Streamlit communities are super helpful!

---

## 🎉 You're Ready!

Run the app now:
```bash
streamlit run app.py
```

Then open your browser to: `http://localhost:8501`

Happy analyzing! 🏁
