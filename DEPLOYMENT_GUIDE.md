# 🌐 Deploying F1 Analytics to nexairi.com

This guide shows you how to integrate the F1 Analytics Dashboard with your website at nexairi.com.

## 🎯 Deployment Options

### Option 1: Subdomain (Recommended)
Host the app on a subdomain like `f1.nexairi.com` or `analytics.nexairi.com`

**Pros:**
- Clean separation
- Easy to manage
- Professional look
- Can use different tech stack

**Cons:**
- Requires DNS configuration
- Needs separate hosting

### Option 2: Embedded iFrame
Embed the Streamlit app in your main website

**Pros:**
- Integrates with existing site
- Single domain
- Easy navigation

**Cons:**
- Performance considerations
- Mobile responsiveness challenges

### Option 3: Full Integration
Rebuild using your website's existing stack (React, Vue, etc.)

**Pros:**
- Seamless integration
- Full control
- Consistent branding

**Cons:**
- Most development work
- Requires frontend expertise

---

## 🚀 Option 1: Subdomain Deployment

### Step 1: Deploy to Streamlit Cloud

1. **Push code to GitHub**:
```bash
cd f1-analytics-app
git init
git add .
git commit -m "Initial F1 Analytics Dashboard"
git remote add origin https://github.com/YOUR-USERNAME/f1-analytics.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**:
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with GitHub
- Click "New app"
- Select your repository
- Click "Deploy"

Your app will be at: `https://YOUR-USERNAME-f1-analytics.streamlit.app`

3. **Set up custom subdomain**:
- In Streamlit Cloud settings, add custom domain
- Or use a reverse proxy (see below)

### Step 2: Configure DNS

In your domain registrar (where you bought nexairi.com):

Add CNAME record:
```
Type: CNAME
Name: f1 (or analytics)
Value: YOUR-USERNAME-f1-analytics.streamlit.app
TTL: 3600
```

**Result**: Your app will be accessible at `f1.nexairi.com`

### Alternative: Use Cloudflare Pages

1. **Deploy to Cloudflare**:
```bash
npm install -g wrangler
wrangler pages project create f1-analytics
wrangler pages deploy dist
```

2. **Configure custom domain**:
- In Cloudflare dashboard
- Pages → Your project → Custom domains
- Add: `f1.nexairi.com`

---

## 🔗 Option 2: iFrame Integration

### Add to your nexairi.com HTML:

```html
<!DOCTYPE html>
<html>
<head>
    <title>F1 Analytics | nexairi.com</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
        }
        
        #f1-app {
            width: 100%;
            height: 100vh;
            border: none;
        }
        
        /* Optional: Add loading spinner */
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <div class="loading">Loading F1 Analytics...</div>
    <iframe 
        id="f1-app"
        src="https://YOUR-APP.streamlit.app"
        onload="document.querySelector('.loading').style.display='none'"
    ></iframe>
</body>
</html>
```

### With Navigation Bar:

```html
<!DOCTYPE html>
<html>
<head>
    <title>F1 Analytics | nexairi.com</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
        }
        
        nav {
            background: #1a1a1a;
            padding: 1rem;
            color: white;
        }
        
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 1rem;
        }
        
        #f1-app {
            width: 100%;
            height: calc(100vh - 60px);
            border: none;
        }
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/f1-analytics">F1 Analytics</a>
        <a href="/about">About</a>
    </nav>
    
    <iframe 
        id="f1-app"
        src="https://YOUR-APP.streamlit.app?embedded=true"
    ></iframe>
</body>
</html>
```

---

## 🔧 Option 3: Full Stack Integration

### Using React/Next.js

If your nexairi.com uses React, you can rebuild the app in React:

```javascript
// pages/f1-analytics.js
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export default function F1Analytics() {
  const [raceData, setRaceData] = useState(null);
  
  useEffect(() => {
    // Fetch data from FastF1 API or your backend
    fetchRaceData();
  }, []);
  
  const fetchRaceData = async () => {
    // Your data fetching logic
    const response = await fetch('/api/f1/race/2024/1');
    const data = await response.json();
    setRaceData(data);
  };
  
  return (
    <div className="f1-analytics">
      <h1>F1 Analytics Dashboard</h1>
      {raceData && (
        <LineChart data={raceData.laps}>
          <XAxis dataKey="lap" />
          <YAxis />
          <Line type="monotone" dataKey="time" stroke="#e10600" />
          <Tooltip />
        </LineChart>
      )}
    </div>
  );
}
```

### Python Backend (FastAPI)

Create an API to serve F1 data to your frontend:

```python
# backend/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nexairi.com"],
    allow_methods=["*"],
)

@app.get("/api/f1/race/{year}/{round}")
async def get_race_data(year: int, round: int):
    session = fastf1.get_session(year, round, 'R')
    session.load()
    
    return {
        "event": session.event.to_dict(),
        "results": session.results.to_dict(),
        "laps": session.laps.to_dict()
    }
```

---

## 🎨 Branding Integration

### Match Your nexairi.com Style

1. **Update colors in app.py**:
```python
st.markdown("""
    <style>
    :root {
        --primary-color: #YOUR_BRAND_COLOR;
        --background-color: #YOUR_BG_COLOR;
    }
    .main-header {
        color: var(--primary-color);
    }
    </style>
""", unsafe_allow_html=True)
```

2. **Add your logo**:
```python
st.image("https://nexairi.com/logo.png", width=200)
```

3. **Custom footer**:
```python
st.markdown("""
    <div style='text-align: center;'>
        <p>© 2026 nexairi.com | All rights reserved</p>
    </div>
""", unsafe_allow_html=True)
```

---

## 📊 Analytics Integration

### Add Google Analytics

```python
# In app.py, add to the head:
st.components.v1.html("""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'GA_MEASUREMENT_ID');
    </script>
""", height=0)
```

---

## 🔒 Security Considerations

1. **HTTPS**: Always use HTTPS for production
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **CORS**: Configure properly if using API backend
4. **API Keys**: Never expose API keys in frontend code

---

## 💰 Cost Estimates

### Free Tier Options:
- **Streamlit Cloud**: Free (with limitations)
- **Vercel**: Free for personal projects
- **Cloudflare Pages**: Free

### Paid Options:
- **AWS EC2**: ~$10-50/month
- **Google Cloud Run**: ~$5-30/month
- **DigitalOcean**: $12-24/month

### Recommended for nexairi.com:
**Streamlit Cloud** ($0) + **Custom Domain** (included with your site)

---

## 📱 Mobile Optimization

The Streamlit app is already mobile-responsive, but for best results:

```python
# Add viewport meta tag
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# Use responsive columns
col1, col2 = st.columns([1, 1])  # Equal width on mobile
```

---

## 🚦 Go Live Checklist

- [ ] Test app locally
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud (or alternative)
- [ ] Configure custom domain
- [ ] Update DNS records
- [ ] Test on mobile devices
- [ ] Add analytics tracking
- [ ] Update nexairi.com navigation
- [ ] Add SSL certificate (automatic with most hosts)
- [ ] Test performance
- [ ] Monitor errors

---

## 🎉 Marketing Your New Feature

### On nexairi.com homepage:

```html
<section class="features">
    <div class="feature">
        <h3>🏎️ F1 Analytics Dashboard</h3>
        <p>AI-powered Formula 1 race analysis and predictions</p>
        <a href="https://f1.nexairi.com">Explore Now →</a>
    </div>
</section>
```

### Social Media Announcement:

> 🚀 New Feature Alert! 
> 
> nexairi.com now features an AI-powered F1 Analytics Dashboard!
> 
> 📊 Analyze every race
> 🏎️ Compare drivers
> 🤖 AI predictions
> 📈 Interactive telemetry
>
> Check it out: https://f1.nexairi.com
>
> #F1 #DataAnalytics #AI

---

## 🆘 Need Help?

- **Streamlit Docs**: https://docs.streamlit.io/
- **FastF1 Docs**: https://docs.fastf1.dev/
- **Deployment Issues**: Check Streamlit community forum
- **Custom Integration**: Consider hiring a developer

---

**Next Steps:**
1. Choose your deployment option
2. Follow the steps above
3. Test thoroughly
4. Go live!
5. Share with the world 🎉
