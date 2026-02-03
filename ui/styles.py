"""UI Styles - Professional F1 Dashboard Styling"""
from config.settings import settings

def get_custom_css() -> str:
    """Get custom CSS for professional, polished application"""
    colors = settings.UI_COLORS
    return f"""
    <style>
    /* Main Header - Bold, Professional */
    .main-header {{
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, {colors['primary_red']} 0%, #c80000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* Subtitle - Elegant and Professional */
    .subtitle {{
        color: {colors['text_secondary']};
        font-size: 1.3rem;
        font-weight: 500;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }}
    
    /* Metric Cards - Clean and Modern */
    .metric-card {{
        background: linear-gradient(135deg, {colors['background_light']} 0%, rgba(200, 0, 0, 0.02) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid {colors['primary_red']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 16px rgba(200, 0, 0, 0.15);
        transform: translateY(-2px);
    }}
    
    /* Section Headers */
    .section-header {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {colors['primary_red']};
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid {colors['primary_red']};
        padding-bottom: 0.5rem;
    }}
    
    /* Data Tables - Professional Look */
    .stDataFrame {{
        border-radius: 8px;
        border: 1px solid rgba(200, 0, 0, 0.1);
    }}
    
    /* Chart Containers - Polished */
    .chart-container {{
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        padding: 1rem;
        margin: 1rem 0;
    }}
    
    /* Buttons - Interactive */
    .stButton > button {{
        background: linear-gradient(135deg, {colors['primary_red']} 0%, #c80000 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        box-shadow: 0 4px 12px rgba(200, 0, 0, 0.3);
        transform: translateY(-2px);
    }}
    
    /* Selectbox - Professional Styling */
    .stSelectbox {{
        border-radius: 6px;
    }}
    
    /* Info Box - Clean Design */
    .info-box {{
        background: linear-gradient(135deg, rgba(200, 0, 0, 0.05) 0%, rgba(200, 0, 0, 0.02) 100%);
        border-left: 4px solid {colors['primary_red']};
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }}
    
    /* Error/Warning - Consistent */
    .error-box {{
        background: #ffe6e6;
        border-left: 4px solid #d32f2f;
        padding: 1rem;
        border-radius: 6px;
        color: #c80000;
    }}
    
    /* Global Text Enhancements */
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        background: #f8f9fa;
    }}
    
    /* Horizontal Line - Professional */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, {colors['primary_red']}, transparent);
        margin: 2rem 0;
    }}
    </style>
    """
