import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# Set page configuration
st.set_page_config(
    page_title="BMW App Review Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:support@example.com',
        'Report a bug': 'mailto:bugs@example.com',
        'About': 'This dashboard visualizes insights from text mining of MyBMW app reviews.'
    }
)

# Dark theme is the only option
is_dark_theme = True

# Custom CSS for styling
st.markdown(f"""
<style>
    /* Main theme colors */
    :root {{
        --background-color: #0E1117;
        --text-color: #FFFFFF;
        --card-bg-color: #1E2130;
        --card-border-color: #2D3748;
        --bmw-blue: #4299E1;
        --accent-color: #4299E1;
        --hover-color: #4A5568;
        --grid-color: rgba(255, 255, 255, 0.1);
    }}

    /* Body styling */
    body {{
        color: var(--text-color);
        background-color: var(--background-color);
    }}

    /* Element styling */
    .main-header {{
        font-size: 2.5rem;
        color: var(--bmw-blue);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
        padding: 1rem 0;
    }}
    .sub-header {{
        font-size: 1.8rem;
        color: var(--text-color);
        margin: 1.2rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }}
    .category-header {{
        font-size: 1.3rem;
        color: var(--bmw-blue);
        margin: 1rem 0;
        font-weight: 600;
    }}
    .card {{
        background-color: var(--card-bg-color);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid var(--card-border-color);
    }}
    .metrics-card {{
        background-color: var(--card-bg-color);
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid var(--card-border-color);
        transition: transform 0.3s;
    }}
    .metrics-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }}
    .metrics-value {{
        font-size: 2rem;
        font-weight: bold;
        color: var(--bmw-blue);
    }}
    .metrics-label {{
        font-size: 1rem;
        color: var(--text-color);
        opacity: 0.8;
    }}
    .highlight {{
        color: var(--bmw-blue);
        font-weight: bold;
    }}
    .stButton button {{
        background-color: var(--bmw-blue);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        transition: all 0.3s;
    }}
    .stButton button:hover {{
        background-color: #0056b3;
        transform: translateY(-2px);
    }}

    /* Adjust Streamlit's native elements */
    .stPlotlyChart {{
        background-color: transparent !important;
        border-radius: 8px;
        padding: 0;
        border: none;
    }}
    
    /* Remove whitespace around plots */
    .js-plotly-plot .plotly .main-svg {{
        background-color: transparent !important;
    }}
    
    .js-plotly-plot .plotly .svg-container {{
        background-color: transparent !important;
    }}
    
    /* Tab styling */
    .css-1r6slb0, .css-1r6slb0:hover {{
        background-color: var(--bmw-blue);
        border: 1px solid var(--bmw-blue);
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--card-bg-color);
        border-right: 1px solid var(--card-border-color);
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1px;
        background-color: var(--card-bg-color);
    }}
    .stTabs [data-baseweb="tab"] {{
        min-width: 160px;
        height: auto !important;
        padding: 10px 15px !important;
        white-space: pre-wrap;
        background-color: var(--card-bg-color);
        border-radius: 4px 4px 0 0;
        border-right: 1px solid var(--card-border-color);
        border-left: 1px solid var(--card-border-color);
        border-top: 1px solid var(--card-border-color);
        color: var(--text-color);
        transition: all 0.3s;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: var(--bmw-blue) !important;
        color: white !important;
        font-weight: bold;
    }}
    /* Remove tab panel border and background that causes empty boxes */
    .stTabs [data-baseweb="tab-panel"] {{
        background-color: transparent;
        border: none;
        padding: 0;
    }}
    
    /* Custom section dividers */
    .section-divider {{
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), transparent);
        margin: 2rem 0;
        border-radius: 2px;
    }}
    
    /* Footer styling */
    .footer {{
        text-align: center;
        color: var(--text-color);
        opacity: 0.7;
        padding: 20px;
        border-top: 1px solid var(--card-border-color);
        margin-top: 2rem;
    }}
    
    /* Fix for plotly legends */
    .legend {{
        background-color: transparent !important;
    }}
    
    /* Style radio buttons */
    .st-cc {{
        color: var(--text-color);
    }}
    
    /* Style select boxes */
    .stSelectbox div[data-baseweb="select"] > div:first-child {{
        background-color: var(--card-bg-color);
        border-color: var(--card-border-color);
    }}
    
    /* Remove white background from plotly tooltip */
    .plotly-notifier {{
        background-color: transparent !important;
    }}
    
    .js-plotly-plot .plotly .modebar-container {{
        background-color: transparent !important;
    }}
    
    g.infolayer {{
        background-color: transparent !important;
    }}
    
    .bg-white {{
        background-color: var(--card-bg-color) !important;
    }}
    
    .modebar {{
        background-color: transparent !important;
    }}
    
    /* Sidebar title styling */
    .sidebar .sidebar-content {{
        background-color: var(--card-bg-color);
    }}
    
    [data-testid="stSidebarNav"] {{
        background-color: var(--card-bg-color);
    }}
    
    /* Ensure consistent padding in sidebar */
    .css-6qob1r {{
        padding: 3rem 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Define plot style based on theme
def get_plot_settings():
    return {
        'plot_bgcolor': 'rgba(14, 17, 23, 0)',  # Transparent with dark theme base
        'paper_bgcolor': 'rgba(14, 17, 23, 0)',  # Transparent with dark theme base
        'font_color': '#FFFFFF',
        'grid_color': 'rgba(255, 255, 255, 0.1)',
        'color_scale': ['#EF5350', '#A9A9A9', '#81C784']  # Red, Grey, Green - Changing orange to grey for neutral
    }

plot_settings = get_plot_settings()

# Update the main header
st.markdown("""
<div style="text-align: center; padding: 20px 0; margin-bottom: 10px;">
    <h1 style="color: #4299E1; font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(66, 153, 225, 0.3);">
        MyBMW App Review Analysis
    </h1>
    <p style="color: #FFFFFF; opacity: 0.8; margin-top: 10px;">
        Insights from text mining and sentiment analysis of user reviews
    </p>
</div>
""", unsafe_allow_html=True)

# Update sidebar title with clearer styling
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);">
    <h2 style="color: #4299E1; margin-bottom: 5px;">Dashboard Filters</h2>
</div>
""", unsafe_allow_html=True)

# Add additional CSS for better styling
additional_css = """
<style>
    /* Enhanced sidebar styling */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom selectbox styling */
    div[data-baseweb="select"] {
        background-color: #1E2130;
        border-radius: 4px;
        border: 1px solid #2D3748;
        color: white;
    }
    
    /* Custom slider styling */
    div[data-testid="stSlider"] {
        padding: 1rem 0;
    }
    
    /* Fix spacing in cards */
    .card h3 {
        margin-top: 0;
    }
    
    /* Add separator between charts */
    .chart-separator {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(66, 153, 225, 0.3), transparent);
        margin: 2rem 0;
    }
    
    /* Make metrics more prominent */
    .metrics-value {
        font-size: 2.5rem;
        text-shadow: 0 0 10px rgba(66, 153, 225, 0.3);
    }
    
    /* Add animation to hover states */
    .card:hover {
        box-shadow: 0 0 15px rgba(66, 153, 225, 0.2);
        transition: all 0.3s ease;
    }
    
    /* Fix plotly tooltips */
    .hovertext .bg {
        fill: rgba(30, 33, 48, 0.9) !important;
        stroke: #4299E1 !important;
    }
    
    .hovertext .text {
        fill: white !important;
    }
    
    /* Fix export section */
    .st-emotion-cache-1wrcr25 {
        background-color: transparent !important;
    }
    
    /* Fix scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1E2130;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4299E1;
        border-radius: 3px;
    }
    
    /* Add highlight effect to active tab */
    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
    }
    
    /* Fix the empty containers/boxes issue */
    div[data-testid="stVerticalBlock"] div[style*="flex-direction: column"] div[data-testid="stVerticalBlock"] {
        background-color: transparent;
        border-radius: 0;
        padding: 0;
        margin-top: 0;
        border: none;
    }
    
    /* Remove any background styling from tab content containers */
    .stTabs [data-baseweb="tab-list"] + div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Ensure no background on tab content */
    .stTabs > div[data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* Style Streamlit containers to look like cards */
    div.stContainer {
        background-color: var(--card-bg-color);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid var(--card-border-color);
    }
    
    /* Center the tab list (new) */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center !important;
        gap: 1px;
        background-color: var(--card-bg-color);
        width: 100%;
    }
</style>
"""
st.markdown(additional_css, unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('bmw_app_analysis/results/bmw_reviews_consolidated_20250504_155236.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please check the path to the CSV file.")
        return None

# Load the data
df = load_data()

if df is None:
    st.stop()

# Sidebar filters section
st.sidebar.title("Filters")

# Filter by date range if date column exists
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df['date'] >= pd.Timestamp(start_date)) & 
                         (df['date'] <= pd.Timestamp(end_date))]
    else:
        filtered_df = df
else:
    filtered_df = df

# Filter by language
if 'language' in df.columns:
    languages = ['All'] + sorted(df['language'].unique().tolist())
    selected_language = st.sidebar.selectbox("Select Language", languages)
    
    if selected_language != 'All':
        filtered_df = filtered_df[filtered_df['language'] == selected_language]

# Filter by star rating
if 'score' in df.columns:
    min_rating = int(filtered_df['score'].min())
    max_rating = int(filtered_df['score'].max())
    
    selected_ratings = st.sidebar.slider(
        "Select Rating Range",
        min_rating, max_rating, (min_rating, max_rating)
    )
    
    filtered_df = filtered_df[(filtered_df['score'] >= selected_ratings[0]) & 
                              (filtered_df['score'] <= selected_ratings[1])]

# Filter by app version if it exists
if 'appVersion' in df.columns:
    # Extract major.minor version
    df['version_str'] = df['appVersion'].apply(
        lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
    )
    filtered_df['version_str'] = filtered_df['appVersion'].apply(
        lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
    )
    
    versions = ['All'] + sorted(filtered_df['version_str'].dropna().unique().tolist(), 
                                key=lambda v: [int(n) for n in v.split('.')])
    selected_version = st.sidebar.selectbox("Select App Version", versions)
    
    if selected_version != 'All':
        filtered_df = filtered_df[filtered_df['version_str'] == selected_version]

# Overview metrics section
# Removing the section divider above Overview
# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Just use plain section header without a card container
st.markdown('<div class="sub-header">Overview</div>', unsafe_allow_html=True)

# Create metrics using a direct approach
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Total Reviews
    value = f"{len(filtered_df):,}"
    st.markdown(f"""
    <div class="metrics-card">
        <div class="metrics-value">{value}</div>
        <div class="metrics-label">Total Reviews</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Average Rating
    if 'score' in filtered_df.columns:
        avg_rating = filtered_df['score'].mean()
        value = f"{avg_rating:.2f}/5"
    else:
        value = "N/A"
    
    st.markdown(f"""
    <div class="metrics-card">
        <div class="metrics-value">{value}</div>
        <div class="metrics-label">Average Rating</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Positive Sentiment
    if 'sentiment' in filtered_df.columns:
        positive_pct = (filtered_df['sentiment'] == 'positive').mean() * 100
        value = f"{positive_pct:.1f}%"
    else:
        value = "N/A"
    
    st.markdown(f"""
    <div class="metrics-card">
        <div class="metrics-value">{value}</div>
        <div class="metrics-label">Positive Sentiment</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Improvement Index
    if 'sentiment' in filtered_df.columns and 'appVersion' in filtered_df.columns and 'version_str' in filtered_df.columns:
        # If version_str doesn't exist, create it
        if 'version_str' not in filtered_df.columns:
            filtered_df['version_str'] = filtered_df['appVersion'].apply(
                lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
            )
        
        # Convert version strings to numeric for sorting
        filtered_df['version_num'] = pd.to_numeric(filtered_df['version_str'], errors='coerce')
        
        # Drop rows with missing version
        version_df = filtered_df.dropna(subset=['version_num'])
        
        if len(version_df) > 0:
            # Get the median version to split into "newer" and "older"
            median_version = version_df['version_num'].median()
            
            # Create period column
            version_df['period'] = np.where(version_df['version_num'] >= median_version, 'recent', 'earlier')
            
            # Calculate sentiment score for each period
            newer_score = (version_df[version_df['period'] == 'recent']['sentiment'] == 'positive').mean()
            older_score = (version_df[version_df['period'] == 'earlier']['sentiment'] == 'positive').mean()
            
            # Calculate the improvement (percent change)
            if older_score > 0:
                improvement = ((newer_score - older_score) / older_score) * 100
                
                # Format the value with a + or - sign
                if improvement > 0:
                    value = f"+{improvement:.1f}%"
                    color = "green"
                elif improvement < 0:
                    value = f"{improvement:.1f}%"
                    color = "red"
                else:
                    value = "0%"
                    color = "white"
            else:
                value = "N/A"
                color = "white"
        else:
            value = "N/A"
            color = "white"
    else:
        value = "N/A"
        color = "white"
    
    st.markdown(f"""
    <div class="metrics-card">
        <div class="metrics-value" style="color: {color};">{value}</div>
        <div class="metrics-label">Improvement Index</div>
    </div>
    """, unsafe_allow_html=True)

# Main content tabs
# Removing the section divider above Key Insights
# st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# Define the function here before it's first used
def format_plotly_fig(fig):
    """Apply consistent styling to any plotly figure"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
    )
    
    # Set transparent background for all subplots
    for axis in fig.layout:
        if axis.startswith('xaxis') or axis.startswith('yaxis'):
            fig.layout[axis].gridcolor = plot_settings['grid_color']
            
    # Add transparent configuration
    fig.update_layout(
        template="plotly_dark" if is_dark_theme else "plotly_white",
        modebar=dict(bgcolor='rgba(0,0,0,0)', color=plot_settings['font_color']),
    )
    
    # Set transparent config
    fig.update_xaxes(showgrid=True, gridcolor=plot_settings['grid_color'])
    fig.update_yaxes(showgrid=True, gridcolor=plot_settings['grid_color'])
    
    return fig

# Use plain section header
st.markdown('<div class="sub-header">Key Insights</div>', unsafe_allow_html=True)

# Create a row for key insights
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    with st.container():
        st.subheader("Rating Distribution")
        
        if 'score' in filtered_df.columns:
            # Round ratings to nearest integer for histogram
            filtered_df['star_rating'] = filtered_df['score'].round().clip(1, 5).astype(int)
            rating_counts = filtered_df['star_rating'].value_counts().sort_index()
            
            # Create star rating labels
            star_labels = {1: "★", 2: "★★", 3: "★★★", 4: "★★★★", 5: "★★★★★"}
            
            # Prepare data for plotting
            ratings_df = pd.DataFrame({
                'Rating': [star_labels[i] for i in rating_counts.index],
                'Count': rating_counts.values,
                'Rating_Num': rating_counts.index
            })
            
            # Define colors for ratings
            rating_colors = {
                1: '#EF5350',  # Red for 1-star
                2: '#FF7043',  # Orange-Red for 2-star
                3: '#FFB74D',  # Orange for 3-star
                4: '#AED581',  # Light Green for 4-star 
                5: '#66BB6A'   # Green for 5-star
            }
            
            # Create bar chart
            fig = px.bar(
                ratings_df,
                x='Rating',
                y='Count',
                color='Rating_Num', 
                color_discrete_map={1: rating_colors[1], 2: rating_colors[2], 
                                    3: rating_colors[3], 4: rating_colors[4], 
                                    5: rating_colors[5]},
                height=300
            )
            
            # Apply consistent formatting
            fig = format_plotly_fig(fig)
            
            # Add count labels above bars
            fig.update_traces(
                texttemplate='%{y:,}',
                textposition='outside',
                cliponaxis=False,
                hovertemplate='%{x}: %{y:,} reviews<extra></extra>'
            )
            
            # Customize layout
            fig.update_layout(
                xaxis_title=None,
                yaxis_title='Number of Reviews',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add context
            pct_high = ((filtered_df['star_rating'] >= 4).sum() / len(filtered_df) * 100)
            pct_low = ((filtered_df['star_rating'] <= 2).sum() / len(filtered_df) * 100)
            
            st.markdown(f"""
            <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                <strong>{pct_high:.1f}%</strong> of reviews are highly positive (4-5 stars), while 
                <strong>{pct_low:.1f}%</strong> are negative (1-2 stars).
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Rating data not available")

with insight_col2:
    with st.container():
        st.subheader("Topic Sentiment by Version")
        
        if 'topics' in filtered_df.columns and 'sentiment' in filtered_df.columns and 'version_str' in filtered_df.columns:
            # Create version groups for comparison (newer vs older versions)
            if 'version_str' not in filtered_df.columns:
                filtered_df['version_str'] = filtered_df['appVersion'].apply(
                    lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
                )
            
            # Filter out rows with missing version
            version_df = filtered_df.dropna(subset=['version_str'])
            
            # Convert version strings to numeric for sorting
            version_df['version_num'] = pd.to_numeric(version_df['version_str'], errors='coerce')
            
            # Find the median version to split into "newer" and "older"
            median_version = version_df['version_num'].median()
            
            # Create period column
            version_df['period'] = np.where(version_df['version_num'] >= median_version, 'recent', 'earlier')
            
            # Function to calculate sentiment polarity
            def get_polarity(df_subset):
                positive = (df_subset['sentiment'] == 'positive').sum()
                negative = (df_subset['sentiment'] == 'negative').sum()
                total = len(df_subset)
                if total > 0:
                    return (positive - negative) / total
                else:
                    return 0
            
            # Get top topics
            all_topics = []
            for topics_str in version_df['topics'].dropna():
                all_topics.extend([topic.strip() for topic in topics_str.split(',')])
            
            top_topics = pd.Series(all_topics).value_counts().head(10).index.tolist()
            
            # Calculate sentiment polarity for each topic and period
            polarity_data = []
            for topic in top_topics:
                # Get reviews for this topic
                topic_reviews = version_df[version_df['topics'].str.contains(topic, na=False)]
                
                # Skip topics with too few reviews
                if len(topic_reviews) < 20:
                    continue
                    
                # Calculate polarity for each period
                recent_polarity = get_polarity(topic_reviews[topic_reviews['period'] == 'recent'])
                earlier_polarity = get_polarity(topic_reviews[topic_reviews['period'] == 'earlier'])
                
                # Calculate the change
                change = recent_polarity - earlier_polarity
                
                polarity_data.append({
                    'topic': topic,
                    'recent_polarity': recent_polarity,
                    'earlier_polarity': earlier_polarity,
                    'change': change,
                    'review_count': len(topic_reviews)
                })
            
            if polarity_data:
                # Convert to DataFrame and sort by absolute change
                polarity_df = pd.DataFrame(polarity_data)
                polarity_df['abs_change'] = polarity_df['change'].abs()
                polarity_df = polarity_df.sort_values('abs_change', ascending=False).head(8)
                
                # Create horizontal bar chart of changes
                fig = go.Figure()
                
                # Add bars for change values
                fig.add_trace(go.Bar(
                    y=polarity_df['topic'],
                    x=polarity_df['change'],
                    orientation='h',
                    marker_color=np.where(polarity_df['change'] >= 0, '#66BB6A', '#EF5350'),
                    hovertemplate='Change: %{x:.2f}<br>Reviews: %{customdata:,}<extra></extra>',
                    customdata=polarity_df['review_count']
                ))
                
                # Apply consistent styling
                fig = format_plotly_fig(fig)
                
                # Add a vertical line at x=0
                fig.add_shape(
                    type='line',
                    x0=0, y0=-0.5,
                    x1=0, y1=len(polarity_df)-0.5,
                    line=dict(color=plot_settings['font_color'], width=1)
                )
                
                # Customize layout
                fig.update_layout(
                    xaxis_title='Sentiment Change (Newer - Older Versions)',
                    xaxis=dict(range=[-1, 1]),
                    yaxis_title=None,
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add interpretation text
                improving_topics = polarity_df[polarity_df['change'] > 0.2]['topic'].tolist()
                declining_topics = polarity_df[polarity_df['change'] < -0.2]['topic'].tolist()
                
                insight_text = ""
                if improving_topics:
                    improving_str = ", ".join(f"<strong>{t}</strong>" for t in improving_topics[:2])
                    insight_text += f"Sentiment is improving in newer versions for {improving_str}. "
                
                if declining_topics:
                    declining_str = ", ".join(f"<strong>{t}</strong>" for t in declining_topics[:2])
                    insight_text += f"Attention needed for {declining_str} with declining sentiment."
                
                if insight_text:
                    st.markdown(f"""
                    <div style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
                        {insight_text}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Not enough data for version-based sentiment analysis")
        else:
            st.info("Topic, sentiment, or version data not available")

# Close the container div for Key Insights
# st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

tabs = st.tabs([
    "📊 Sentiment Analysis", 
    "🏷️ Topic Distribution", 
    "🌍 Language Analysis",
    "📱 Version Trends", 
    "🚗 Competitors",
    "💡 Feature Requests"
])

# TAB 1: SENTIMENT ANALYSIS
with tabs[0]:
    # Use plain category header
    st.markdown('<div class="category-header">Sentiment Distribution & Trends</div>', unsafe_allow_html=True)
    
    # Row for Sentiment Distribution and Sentiment by Rating
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.subheader("Sentiment Distribution")
            
            if 'sentiment' in filtered_df.columns:
                # Calculate sentiment distribution
                sentiment_counts = filtered_df['sentiment'].value_counts()
                total_reviews = len(filtered_df)
                
                # Define the order we want
                ordered_sentiments = ['negative', 'neutral', 'positive']
                
                # Prepare percentages with consistent order
                percentages = []
                for sentiment in ordered_sentiments:
                    if sentiment in sentiment_counts:
                        count = sentiment_counts[sentiment]
                    else:
                        count = 0
                    percentages.append((count / total_reviews * 100))
                
                # Create a DataFrame for plotting
                sentiment_df = pd.DataFrame({
                    'Sentiment': [s.capitalize() for s in ordered_sentiments],
                    'Percentage': percentages
                })
                
                # Define colors for sentiment
                sentiment_colors = {
                    'Negative': plot_settings['color_scale'][0],
                    'Neutral': plot_settings['color_scale'][1],
                    'Positive': plot_settings['color_scale'][2]
                }
                
                # Create the plotly bar chart
                fig = px.bar(
                    sentiment_df, 
                    x='Sentiment', 
                    y='Percentage',
                    text=[f"{p:.1f}%" for p in percentages],
                    color='Sentiment',
                    color_discrete_map=sentiment_colors,
                    height=400
                )
                
                # Apply the formatting function
                fig = format_plotly_fig(fig)
                
                # Additional layout options specific to this chart
                fig.update_layout(
                    xaxis_title=None,
                    yaxis_title='Percentage of Reviews',
                    yaxis=dict(range=[0, max(percentages) * 1.1]),
                    showlegend=False
                )
                
                # Text positioning
                fig.update_traces(
                    textposition='outside',
                    textfont=dict(size=12, color=plot_settings['font_color']),
                    marker_line_color='rgba(0,0,0,0)',
                    marker_line_width=0
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sentiment data not available")
    
    with col2:
        with st.container():
            st.subheader("Sentiment by Star Rating")
            
            if 'sentiment' in filtered_df.columns and 'score' in filtered_df.columns:
                # Round scores into the 1-to-5 range and count reviews by rating × sentiment
                filtered_df['star_rating'] = filtered_df['score'].round().clip(1, 5).astype(int)
                grouped = (
                    filtered_df.groupby(['star_rating', 'sentiment'])
                        .size()
                        .unstack(fill_value=0)
                        .reindex(columns=['positive', 'neutral', 'negative'], fill_value=0)  # ensure consistent order
                )
                
                # Create stacked bar chart using plotly
                fig = go.Figure()
                
                sentiment_colors = {
                    'negative': plot_settings['color_scale'][0],
                    'neutral': plot_settings['color_scale'][1],
                    'positive': plot_settings['color_scale'][2]
                }
                
                # Add traces for each sentiment (in reverse order so negative is at bottom)
                for sentiment in ['positive', 'neutral', 'negative']:
                    fig.add_trace(go.Bar(
                        x=grouped.index,
                        y=grouped[sentiment],
                        name=sentiment.capitalize(),
                        marker_color=sentiment_colors[sentiment],
                        hovertemplate='%{y:,} reviews<extra></extra>'
                    ))
                
                # Apply the formatting function
                fig = format_plotly_fig(fig)
                
                # Additional layout options specific to this chart
                fig.update_layout(
                    barmode='stack',
                    xaxis=dict(
                        title='Star Rating',
                        tickmode='array',
                        tickvals=list(range(1, 6)),
                        ticktext=['1', '2', '3', '4', '5']
                    ),
                    yaxis=dict(
                        title='Number of Reviews'
                    ),
                    legend=dict(
                        title='Sentiment',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    ),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sentiment or rating data not available")
                
    # New Sentiment Timeline chart
    with st.container():
        st.subheader("Sentiment Timeline")
        
        if 'sentiment' in filtered_df.columns and 'appVersion' in filtered_df.columns:
            # Make sure we have version information
            if 'version_str' not in filtered_df.columns:
                filtered_df['version_str'] = filtered_df['appVersion'].apply(
                    lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
                )
            
            # Convert version strings to numeric for sorting
            filtered_df['version_num'] = pd.to_numeric(filtered_df['version_str'], errors='coerce')
            
            # Drop rows with missing versions
            version_df = filtered_df.dropna(subset=['version_num'])
            
            if len(version_df) > 0:
                # Group by version and calculate sentiment percentages
                version_sentiment = version_df.groupby(['version_str', 'sentiment']).size().unstack(fill_value=0)
                
                # Calculate percentages
                version_total = version_sentiment.sum(axis=1)
                version_pct = version_sentiment.div(version_total, axis=0) * 100
                
                # Reset index to use version as a column
                version_pct = version_pct.reset_index()
                
                # Sort by version number for proper timeline
                version_pct['version_num'] = pd.to_numeric(version_pct['version_str'], errors='coerce')
                version_pct = version_pct.sort_values('version_num')
                
                # Ensure we have all sentiments
                for sentiment in ['positive', 'neutral', 'negative']:
                    if sentiment not in version_pct.columns:
                        version_pct[sentiment] = 0
                
                # Create a plotly line chart
                fig = go.Figure()
                
                # Define colors for sentiment
                sentiment_colors = {
                    'negative': plot_settings['color_scale'][0],
                    'neutral': plot_settings['color_scale'][1],
                    'positive': plot_settings['color_scale'][2]
                }
                
                # Add a line for each sentiment
                for sentiment in ['positive', 'neutral', 'negative']:
                    fig.add_trace(go.Scatter(
                        x=version_pct['version_str'],
                        y=version_pct[sentiment],
                        mode='lines+markers',
                        name=sentiment.capitalize(),
                        line=dict(color=sentiment_colors[sentiment], width=3),
                        marker=dict(size=8),
                        hovertemplate='%{y:.1f}%<extra></extra>'
                    ))
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Update layout
                fig.update_layout(
                    xaxis=dict(
                        title='App Version',
                        tickangle=45,
                        categoryorder='array',
                        categoryarray=version_pct['version_str']
                    ),
                    yaxis=dict(
                        title='Percentage of Reviews',
                        range=[0, 100]
                    ),
                    legend=dict(
                        title='Sentiment',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    ),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.markdown("""
                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                    <p><strong>💡 Insight:</strong> This timeline shows how sentiment has changed across app versions. Sharp drops in positive sentiment or spikes in negative sentiment may indicate issues with specific app updates or features.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Not enough version data available for timeline analysis")
        else:
            st.info("Sentiment or app version data not available for timeline analysis")

# TAB 2: TOPIC ANALYSIS
with tabs[1]:
    # Use plain category header
    st.markdown('<div class="category-header">Topic Distribution & Sentiment</div>', unsafe_allow_html=True)
    
    # Topic Distribution
    if 'topics' in filtered_df.columns:
        with st.container():
            st.subheader("Most Common Topics in Reviews")
            
            # Extract and count all topics (handling comma-separated topics)
            all_topics = []
            for topics_str in filtered_df['topics'].dropna():
                all_topics.extend([topic.strip() for topic in topics_str.split(',')])
            
            # Count topics and get top 15
            topic_counts = pd.Series(all_topics).value_counts().head(15)
            
            # Create a DataFrame for plotting
            topic_df = pd.DataFrame({
                'Topic': topic_counts.index,
                'Count': topic_counts.values
            })
            
            # Create the plotly bar chart
            fig = px.bar(
                topic_df, 
                x='Count', 
                y='Topic',
                orientation='h',
                color='Count',
                color_continuous_scale='Blues',
                height=600
            )
            
            # Apply consistent formatting
            fig = format_plotly_fig(fig)
            
            # Add count labels
            fig.update_traces(
                texttemplate='%{x:,}',
                textposition='outside',
                cliponaxis=False,
                hovertemplate='%{y}: %{x:,} reviews<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Topic Sentiment Analysis
            if 'sentiment' in filtered_df.columns:
                st.subheader("Topic Sentiment Analysis")
                
                # Create a dictionary to store sentiment breakdown for each topic
                topic_sentiment = {}
                
                # For each topic, calculate the sentiment distribution
                for topic in filtered_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                    # Get reviews with this topic
                    topic_reviews = filtered_df[filtered_df['topics'].str.contains(topic, na=False)]
                    
                    # Only include topics with a minimum number of reviews
                    if len(topic_reviews) >= 20:  # Threshold can be adjusted
                        # Count reviews by sentiment
                        sentiment_counts = topic_reviews['sentiment'].value_counts()
                        topic_sentiment[topic] = sentiment_counts
                
                # Convert to DataFrame
                topic_sentiment_df = pd.DataFrame(topic_sentiment).fillna(0).T
                
                # Ensure all sentiments are present
                for sentiment in ['positive', 'neutral', 'negative']:
                    if sentiment not in topic_sentiment_df.columns:
                        topic_sentiment_df[sentiment] = 0
                
                # Calculate total reviews per topic for sorting
                topic_sentiment_df['total'] = topic_sentiment_df.sum(axis=1)
                
                # Sort by total and take top 15
                topic_sentiment_df = topic_sentiment_df.sort_values('total', ascending=False).head(15)
                
                # Calculate percentages for plotting
                for sentiment in ['positive', 'neutral', 'negative']:
                    topic_sentiment_df[f'{sentiment}_pct'] = (topic_sentiment_df[sentiment] / topic_sentiment_df['total'] * 100).round(1)
                
                # Create stacked bar chart using plotly
                fig = go.Figure()
                
                sentiment_colors = {
                    'positive': plot_settings['color_scale'][2],
                    'neutral': plot_settings['color_scale'][1],
                    'negative': plot_settings['color_scale'][0]
                }
                
                # Add traces for each sentiment
                for sentiment in ['positive', 'neutral', 'negative']:
                    fig.add_trace(go.Bar(
                        y=topic_sentiment_df.index,
                        x=topic_sentiment_df[f'{sentiment}_pct'],
                        name=sentiment.capitalize(),
                        orientation='h',
                        marker_color=sentiment_colors[sentiment],
                        hovertemplate='%{x:.1f}%<extra></extra>'
                    ))
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Update layout
                fig.update_layout(
                    barmode='stack',
                    xaxis=dict(
                        title='Percentage of Reviews',
                        range=[0, 100],
                    ),
                    yaxis=dict(
                        title=None,
                        autorange="reversed",  # Reverse to match the topic distribution chart
                    ),
                    legend=dict(
                        title='Sentiment',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    ),
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add a sentiment polarity index chart
                st.subheader("Sentiment Polarity by Topic")
                
                # Calculate sentiment polarity
                topic_sentiment_df['polarity'] = (topic_sentiment_df['positive'] - topic_sentiment_df['negative']) / topic_sentiment_df['total']
                
                # Sort by polarity
                polarity_df = topic_sentiment_df.sort_values('polarity', ascending=False)
                
                # Create a DataFrame for plotting
                plot_df = pd.DataFrame({
                    'Topic': polarity_df.index,
                    'Polarity': polarity_df['polarity'],
                    'Total Reviews': polarity_df['total']
                })
                
                # Create the plotly bar chart
                fig = px.bar(
                    plot_df, 
                    x='Polarity', 
                    y='Topic',
                    orientation='h',
                    color='Polarity',
                    color_continuous_scale=['#F44336', '#FFFFFF', '#4CAF50'],  # Red to White to Green
                    range_color=[-1, 1],
                    height=600,
                    hover_data=['Total Reviews']
                )
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Add a vertical line at x=0
                fig.add_shape(
                    type='line',
                    x0=0, y0=-0.5,
                    x1=0, y1=len(plot_df)-0.5,
                    line=dict(color=plot_settings['font_color'], width=1)
                )
                
                # Update layout
                fig.update_layout(
                    xaxis_title='Sentiment Polarity (positive-negative)/total',
                    xaxis=dict(range=[-1, 1]),
                    yaxis_title=None,
                    yaxis=dict(autorange="reversed"),
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        # Add Topic Complexity analysis
        with st.container():
            st.subheader("Topic Complexity (Review Length Analysis)")
            
            if 'topics' in filtered_df.columns and 'content' in filtered_df.columns:
                # Add character count to each review
                filtered_df['review_length'] = filtered_df['content'].astype(str).apply(len)
                
                # Calculate average length by topic
                topic_length_data = []
                
                for topic in filtered_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                    # Get reviews with this topic
                    topic_reviews = filtered_df[filtered_df['topics'].str.contains(topic, na=False)]
                    
                    # Only include topics with a minimum number of reviews
                    if len(topic_reviews) >= 20:  # Threshold can be adjusted
                        # Calculate average length
                        avg_length = topic_reviews['review_length'].mean()
                        median_length = topic_reviews['review_length'].median()
                        review_count = len(topic_reviews)
                        
                        topic_length_data.append({
                            'topic': topic,
                            'avg_length': avg_length,
                            'median_length': median_length,
                            'review_count': review_count
                        })
                
                # Convert to DataFrame and sort
                if topic_length_data:
                    length_df = pd.DataFrame(topic_length_data)
                    length_df = length_df.sort_values('avg_length', ascending=False).head(15)
                    
                    # Create the plotly bar chart
                    fig = px.bar(
                        length_df,
                        y='topic',
                        x='avg_length',
                        orientation='h',
                        color='avg_length',
                        color_continuous_scale='Viridis',
                        hover_data=['review_count', 'median_length'],
                        height=500,
                        labels={
                            'avg_length': 'Average Review Length (characters)',
                            'topic': 'Topic',
                            'review_count': 'Number of Reviews',
                            'median_length': 'Median Length'
                        }
                    )
                    
                    # Apply consistent formatting
                    fig = format_plotly_fig(fig)
                    
                    # Add count labels
                    fig.update_traces(
                        texttemplate='%{x:.0f}',
                        textposition='outside',
                        cliponaxis=False,
                        hovertemplate='%{y}: %{x:.0f} chars<br>Reviews: %{customdata[0]}<br>Median: %{customdata[1]:.0f} chars<extra></extra>'
                    )
                    
                    # Update layout
                    fig.update_layout(
                        xaxis=dict(title='Average Review Length (characters)'),
                        yaxis=dict(title=None, autorange="reversed"),
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate the overall average for comparison
                    overall_avg = filtered_df['review_length'].mean()
                    
                    # Add explanation
                    st.markdown(f"""
                    <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                        <p><strong>💡 Insight:</strong> Topics with longer average review lengths often represent more complex issues or features that users feel compelled to explain in detail. The overall average review length is <strong>{overall_avg:.0f}</strong> characters.</p>
                        <p>Topics like <strong>{length_df.iloc[0]['topic']}</strong> and <strong>{length_df.iloc[1]['topic']}</strong> have significantly longer reviews, which may indicate areas where users are experiencing complex issues or have detailed feedback.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Not enough data for topic complexity analysis")
            else:
                st.info("Review content or topic data not available for complexity analysis")
    else:
        st.info("Topic data not available")

# TAB 3: LANGUAGE ANALYSIS
with tabs[2]:
    # Use plain category header
    st.markdown('<div class="category-header">Ratings by Language and Topic</div>', unsafe_allow_html=True)
    
    if 'language' in filtered_df.columns and 'topics' in filtered_df.columns and 'score' in filtered_df.columns:
        # Add Average Rating by Language plot
        with st.container():
            st.subheader("Average Rating by Language")
            
            # Calculate average rating by language
            lang_ratings = filtered_df.groupby('language')['score'].agg(['mean', 'count']).reset_index()
            lang_ratings = lang_ratings.rename(columns={'mean': 'avg_rating'})
            
            # Sort by average rating
            lang_ratings = lang_ratings.sort_values('avg_rating', ascending=False)
            
            # Filter to languages with enough reviews
            min_reviews = 10
            lang_ratings = lang_ratings[lang_ratings['count'] >= min_reviews]
            
            if len(lang_ratings) > 0:
                # Create the bar chart
                fig = px.bar(
                    lang_ratings,
                    x='language',
                    y='avg_rating',
                    color='avg_rating',
                    color_continuous_scale='RdYlGn',
                    range_color=[1, 5],
                    labels={'language': 'Language', 'avg_rating': 'Average Rating', 'count': 'Number of Reviews'},
                    hover_data=['count'],
                    height=400
                )
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Add rating labels
                fig.update_traces(
                    texttemplate='%{y:.2f}',
                    textposition='outside',
                    cliponaxis=False,
                    hovertemplate='%{x}: %{y:.2f} avg rating<br>Based on %{customdata[0]:,} reviews<extra></extra>'
                )
                
                # Update layout
                fig.update_layout(
                    xaxis_title='Language',
                    yaxis_title='Average Rating',
                    yaxis=dict(range=[0, 5.5]),
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.markdown("""
                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                    <p><strong>💡 Insight:</strong> This chart shows average app ratings across different languages, indicating how user satisfaction varies by language/region. 
                    Significant differences may point to localization issues, cultural preferences, or regional feature disparities.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Not enough language data for average rating analysis")
        
        # Add Most Discussed Topics per Language
        with st.container():
            st.subheader("Most Discussed Topics per Language")
            
            # Get top languages
            top_languages = filtered_df['language'].value_counts().head(5).index.tolist()
            
            # Process topics by language
            language_topics = {}
            
            for language in top_languages:
                # Get reviews for this language
                lang_reviews = filtered_df[filtered_df['language'] == language]
                
                # Extract topics
                all_topics = []
                for topics_str in lang_reviews['topics'].dropna():
                    all_topics.extend([topic.strip() for topic in topics_str.split(',')])
                
                # Count topics
                topic_counts = pd.Series(all_topics).value_counts()
                
                # Get top 5 topics
                top_topics = topic_counts.head(5)
                
                # Store in dictionary
                language_topics[language] = top_topics
            
            # Create a DataFrame for plotting
            plot_data = []
            
            for language, topics in language_topics.items():
                for topic, count in topics.items():
                    plot_data.append({
                        'language': language,
                        'topic': topic,
                        'count': count
                    })
            
            # Convert to DataFrame
            if plot_data:
                topics_df = pd.DataFrame(plot_data)
                
                # Create grouped bar chart
                fig = px.bar(
                    topics_df,
                    x='language',
                    y='count',
                    color='topic',
                    barmode='group',
                    height=500,
                    labels={'language': 'Language', 'count': 'Number of Reviews', 'topic': 'Topic'}
                )
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Update layout
                fig.update_layout(
                    xaxis_title='Language',
                    yaxis_title='Number of Reviews',
                    legend=dict(
                        title='Topic',
                        orientation='h',
                        yanchor='bottom',
                        y=1.02,
                        xanchor='right',
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.markdown("""
                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                    <p><strong>💡 Insight:</strong> This chart shows which topics are most discussed in each language, revealing how priorities and concerns vary across different user regions. 
                    Language-specific topics may indicate localization needs or regional feature preferences that should be addressed.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Not enough topic data for language-specific analysis")
                
        with st.container():
            st.subheader("Rating by Language and Topic")
            
            # Identify the top 10 languages
            language_counts = filtered_df['language'].value_counts().head(10)
            top_languages = language_counts.index.tolist()
            
            # Get the top 10 topics
            all_topics = []
            for topics_str in filtered_df['topics'].dropna():
                all_topics.extend([topic.strip() for topic in topics_str.split(',')])
            
            top_topics = pd.Series(all_topics).value_counts().head(10).index.tolist()
            
            # Create a DataFrame to store average ratings
            ratings_matrix = pd.DataFrame(index=top_topics, columns=top_languages)
            
            # Fill the matrix with average ratings
            for topic in top_topics:
                for language in top_languages:
                    # Filter reviews for this topic and language
                    mask = (filtered_df['topics'].str.contains(topic, na=False)) & (filtered_df['language'] == language)
                    reviews = filtered_df[mask]
                    
                    # Calculate average rating if there are reviews
                    if len(reviews) > 0:
                        avg_rating = reviews['score'].mean().round(1)
                        ratings_matrix.loc[topic, language] = float(avg_rating)
                    else:
                        # Leave as NaN
                        pass
            
            # Convert to numeric values explicitly
            ratings_matrix = ratings_matrix.apply(pd.to_numeric, errors='coerce')
            
            # Create the heatmap using plotly
            fig = px.imshow(
                ratings_matrix,
                labels=dict(x="Language", y="Topic", color="Average Rating"),
                x=ratings_matrix.columns,
                y=ratings_matrix.index,
                color_continuous_scale="RdYlGn",
                range_color=[1, 5],
                height=600,
                aspect="auto"
            )
            
            # Add text annotations
            annotations = []
            for i, topic in enumerate(ratings_matrix.index):
                for j, language in enumerate(ratings_matrix.columns):
                    if not pd.isna(ratings_matrix.iloc[i, j]):
                        annotations.append(
                            dict(
                                x=j,
                                y=i,
                                text=str(ratings_matrix.iloc[i, j]),
                                showarrow=False,
                                font=dict(color="black")
                            )
                        )
            
            # Apply consistent formatting
            fig = format_plotly_fig(fig)
            
            fig.update_layout(annotations=annotations)
            fig.update_layout(
                xaxis=dict(tickangle=45),
                coloraxis_colorbar=dict(
                    title="Avg. Rating",
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=["1", "2", "3", "4", "5"]
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.markdown("""
            <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                <p><strong>💡 Insight:</strong> This heatmap shows how different topics are rated across languages. 
                Higher average ratings (green) indicate more positive reception, while lower ratings (red) suggest areas for improvement in specific languages.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Language, topic, or rating data not available for language analysis")

# TAB 4: VERSION TRENDS
with tabs[3]:
    # Use plain category header
    st.markdown('<div class="category-header">Sentiment Trends Across App Versions</div>', unsafe_allow_html=True)
    
    if 'appVersion' in filtered_df.columns and 'topics' in filtered_df.columns and 'sentiment' in filtered_df.columns:
        with st.container():
            st.subheader("Sentiment Trends by Topic Across App Versions")
            
            # Extract version information if not already done
            if 'version_str' not in filtered_df.columns:
                filtered_df['version_str'] = filtered_df['appVersion'].apply(
                    lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
                )
            
            # Identify significant topics
            significant_topics = []
            topic_counts = {}
            
            for topics_str in filtered_df['topics'].dropna():
                topics = [topic.strip() for topic in topics_str.split(',')]
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Take top 10 topics with at least 50 reviews
            significant_topics = [topic for topic, count in 
                                sorted(topic_counts.items(), key=lambda x: x[1], reverse=True) 
                                if count >= 50][:10]
            
            # Get unique versions ordered chronologically
            filtered_df['version_num'] = pd.to_numeric(filtered_df['version_str'], errors='coerce')
            unique_versions = filtered_df.dropna(subset=['version_num']).sort_values('version_num')['version_str'].unique()
            
            if len(unique_versions) >= 2:  # Need at least 2 versions for trend analysis
                # Process data for each topic and version
                polarity_data = {}
                
                for topic in significant_topics:
                    polarity_by_version = []
                    
                    for version in unique_versions:
                        # Get reviews for this topic and version
                        topic_version_mask = (filtered_df['version_str'] == version) & (filtered_df['topics'].str.contains(topic, na=False))
                        topic_version_reviews = filtered_df[topic_version_mask]
                        
                        # Calculate polarity if enough reviews
                        if len(topic_version_reviews) >= 10:
                            pos = (topic_version_reviews['sentiment'] == 'positive').sum()
                            neg = (topic_version_reviews['sentiment'] == 'negative').sum()
                            total = len(topic_version_reviews)
                            polarity = (pos - neg) / total
                            polarity_by_version.append((version, polarity))
                    
                    # Only include topics with data for at least 3 versions
                    if len(polarity_by_version) >= 3:
                        polarity_data[topic] = polarity_by_version
                
                if polarity_data:  # Only proceed if we have data to show
                    # Calculate average sentiment to sort topics
                    topic_avg_sentiment = {}
                    for topic, data in polarity_data.items():
                        values = [p for _, p in data]
                        if values:
                            topic_avg_sentiment[topic] = sum(values) / len(values)
                    
                    # Sort topics by average sentiment
                    sorted_topics = sorted(topic_avg_sentiment.items(), key=lambda x: x[1])
                    topics_to_plot = [t for t, _ in sorted_topics]
                    
                    # Create mapping from version string to x position for equal spacing
                    version_positions = {v: i for i, v in enumerate(unique_versions)}
                    
                    # Create plotly line chart
                    fig = go.Figure()
                    
                    # Use a distinct color palette
                    colors = px.colors.qualitative.Plotly[:len(topics_to_plot)]
                    line_styles = ['solid', 'dash', 'dot', 'dashdot'] * 10  # Reuse line styles as needed
                    
                    # Plot each topic
                    for i, topic in enumerate(topics_to_plot):
                        # Extract data points and map versions to positions
                        data_points = polarity_data[topic]
                        
                        # Map version strings to x positions and sort by position
                        x_versions = [v for v, p in data_points]
                        x_pos = [version_positions[v] for v in x_versions]
                        y_vals = [p for _, p in data_points]
                        
                        # Sort by x position
                        points = sorted(zip(x_pos, y_vals, x_versions))
                        x_pos = [p[0] for p in points]
                        y_vals = [p[1] for p in points]
                        x_versions = [p[2] for p in points]
                        
                        fig.add_trace(go.Scatter(
                            x=x_versions,
                            y=y_vals,
                            mode='lines+markers',
                            name=topic,
                            line=dict(
                                color=colors[i % len(colors)],
                                dash=line_styles[i % len(line_styles)],
                                width=2
                            ),
                            marker=dict(size=8)
                        ))
                    
                    # Add horizontal line at y=0
                    fig.add_shape(
                        type="line",
                        x0=unique_versions[0],
                        y0=0,
                        x1=unique_versions[-1],
                        y1=0,
                        line=dict(color=plot_settings['font_color'], width=1, dash="dash")
                    )
                    
                    # Shade regions for positive and negative sentiment
                    # This is done by adding filled area traces
                    x_range = list(unique_versions)
                    
                    # Add positive region (green)
                    fig.add_trace(go.Scatter(
                        x=x_range + x_range[::-1],
                        y=[0] * len(x_range) + [1] * len(x_range),
                        fill="toself",
                        fillcolor="rgba(76, 175, 80, 0.1)",
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo="skip"
                    ))
                    
                    # Add negative region (red)
                    fig.add_trace(go.Scatter(
                        x=x_range + x_range[::-1],
                        y=[0] * len(x_range) + [-1] * len(x_range),
                        fill="toself",
                        fillcolor="rgba(244, 67, 54, 0.1)",
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo="skip"
                    ))
                    
                    # Apply consistent formatting
                    fig = format_plotly_fig(fig)
                    
                    # Update layout
                    fig.update_layout(
                        title=None,
                        xaxis_title="App Version",
                        yaxis_title="Sentiment Polarity (positive-negative)/total",
                        legend=dict(
                            title="Topics",
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=1.01
                        ),
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                        <p><strong>💡 Insight:</strong> This chart shows how sentiment for different topics has changed across app versions. 
                        Upward trends indicate improving reception, while downward trends may highlight areas needing attention.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Not enough version data available for trend analysis")
            else:
                st.info("Not enough app versions available for trend analysis")
        
        # Add Fix Effectiveness Analysis
        with st.container():
            st.subheader("Fix Effectiveness Analysis")
            
            # Make sure we have version information
            if 'version_str' in filtered_df.columns and 'version_num' in filtered_df.columns:
                # Get unique versions ordered chronologically
                versions_ordered = filtered_df.dropna(subset=['version_num']).sort_values('version_num')['version_str'].unique()
                
                if len(versions_ordered) >= 2:  # Need at least 2 versions for comparison
                    # Find only the latest version transition
                    latest_version = versions_ordered[-1]
                    previous_version = versions_ordered[-2]
                    
                    # Calculate how sentiment changed for each topic during this version transition
                    topic_improvements = []
                    
                    for topic in filtered_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                        # Get reviews for this topic in each version
                        prev_reviews = filtered_df[(filtered_df['version_str'] == previous_version) & 
                                                (filtered_df['topics'].str.contains(topic, na=False))]
                        latest_reviews = filtered_df[(filtered_df['version_str'] == latest_version) & 
                                                  (filtered_df['topics'].str.contains(topic, na=False))]
                        
                        # Only analyze if we have enough reviews
                        if len(prev_reviews) >= 15 and len(latest_reviews) >= 15:
                            # Calculate negative sentiment percentage for each version
                            prev_neg_pct = (prev_reviews['sentiment'] == 'negative').mean() * 100
                            latest_neg_pct = (latest_reviews['sentiment'] == 'negative').mean() * 100
                            
                            # Calculate improvement
                            if prev_neg_pct > 20:  # Only consider topics that had a significant problem
                                reduction = prev_neg_pct - latest_neg_pct
                                reduction_pct = (reduction / prev_neg_pct) * 100 if prev_neg_pct > 0 else 0
                                
                                if reduction > 0:  # Only include improvements
                                    topic_improvements.append({
                                        'topic': topic,
                                        'from_version': previous_version,
                                        'to_version': latest_version,
                                        'from_neg_pct': prev_neg_pct,
                                        'to_neg_pct': latest_neg_pct,
                                        'reduction': reduction,
                                        'reduction_pct': reduction_pct,
                                        'from_reviews': len(prev_reviews),
                                        'to_reviews': len(latest_reviews)
                                    })
                
                    # Convert to DataFrame and find the top improvements
                    if topic_improvements:
                        improvements_df = pd.DataFrame(topic_improvements)
                        top_improvements = improvements_df.sort_values('reduction_pct', ascending=False).head(10)
                        
                        # Create a DataFrame for plotting
                        plot_data = []
                        for _, row in top_improvements.iterrows():
                            plot_data.append({
                                'topic': row['topic'],
                                'version_transition': f"{row['from_version']} → {row['to_version']}",
                                'reduction_pct': row['reduction_pct'],
                                'from_neg_pct': row['from_neg_pct'],
                                'to_neg_pct': row['to_neg_pct'],
                                'from_reviews': row['from_reviews'],
                                'to_reviews': row['to_reviews']
                            })
                        
                        plot_df = pd.DataFrame(plot_data)
                        
                        # Create the plotly bar chart
                        fig = px.bar(
                            plot_df,
                            x='reduction_pct',
                            y='topic',
                            color='reduction_pct',
                            color_continuous_scale='Greens',
                            hover_data=['version_transition', 'from_neg_pct', 'to_neg_pct', 'from_reviews', 'to_reviews'],
                            height=500,
                            labels={
                                'reduction_pct': 'Negative Sentiment Reduction (%)',
                                'topic': 'Topic',
                                'version_transition': 'Version Transition',
                                'from_neg_pct': 'Initial Negative %',
                                'to_neg_pct': 'Final Negative %',
                                'from_reviews': 'Initial Reviews',
                                'to_reviews': 'Final Reviews'
                            }
                        )
                        
                        # Apply consistent formatting
                        fig = format_plotly_fig(fig)
                        
                        # Add labels
                        fig.update_traces(
                            texttemplate='%{x:.1f}%',
                            textposition='outside',
                            cliponaxis=False,
                            hovertemplate='%{y}<br>%{customdata[0]}<br>Initial: %{customdata[1]:.1f}% → Final: %{customdata[2]:.1f}%<br>Reviews: %{customdata[3]} → %{customdata[4]}<extra></extra>'
                        )
                        
                        # Update layout
                        fig.update_layout(
                            xaxis_title='Negative Sentiment Reduction (%)',
                            yaxis_title=None,
                            coloraxis_showscale=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add explanation
                        reduction_pct_text = f"{plot_df.iloc[0]['reduction_pct']:.1f}%" if len(plot_df) > 0 else "N/A"
                        topic_text = plot_df.iloc[0]['topic'] if len(plot_df) > 0 else "N/A"
                        
                        st.markdown(f"""
                        <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                            <p><strong>💡 Insight:</strong> This chart shows which topics saw the greatest reduction in negative sentiment in the most recent update from version <strong>{previous_version}</strong> to <strong>{latest_version}</strong>, indicating effective fixes.</p>
                            <p>The greatest improvement was seen for the topic <strong>{topic_text}</strong>, with a <strong>{reduction_pct_text}</strong> reduction in negative sentiment.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info(f"No significant improvements found between versions {previous_version} and {latest_version}")
                else:
                    st.info("At least 2 versions are needed for fix effectiveness analysis")
            else:
                st.info("Version data not available for fix effectiveness analysis")
    else:
        st.info("App version, topic, or sentiment data not available for version trend analysis")

# TAB 5: COMPETITOR ANALYSIS
with tabs[4]:
    # Use plain category header
    st.markdown('<div class="category-header">Competitor Mentions in App Reviews</div>', unsafe_allow_html=True)
    
    if 'competitor_mentioned' in filtered_df.columns:
        with st.container():
            st.subheader("Most Frequently Mentioned Competitors")
            
            # Define allowed competitors (automobile manufacturers only)
            allowed_competitors = [
                'mercedes', 'tesla', 'audi', 'volvo', 'volkswagen', 'dacia', 'peugeot', 
                'škoda', 'mini', 'kia', 'renault', 'ford', 'land rover', 'toyota', 
                'citroën', 'jaguar', 'porsche', 'seat', 'fiat', 'lexus', 'cupra', 
                'smart', 'opel', 'chevrolet', 'mazda', 'polestar', 'yugo', 'hyundai', 
                'nissan', 'alpina'
            ]
            
            # Define mapping for variant names
            variant_mapping = {
                'vw': 'volkswagen',
                'skoda': 'škoda',
                'citroen': 'citroën'
            }
            
            # Function to parse and extract competitors
            def extract_competitors(competitor_str):
                if pd.isna(competitor_str) or str(competitor_str).lower() == 'none':
                    return []
                
                # Convert to lowercase for consistency
                competitor_str = str(competitor_str).lower()
                
                # Handle compound mentions by splitting on common separators
                competitors = re.split(r'\s+and\s+|\s*,\s*|\s*&\s*|\s+plus\s+|\s+with\s+', competitor_str)
                
                # Clean up and filter to allowed competitors only
                filtered_competitors = []
                
                for comp in competitors:
                    comp = comp.strip()
                    if comp:
                        # Apply mapping for variants
                        if comp in variant_mapping:
                            comp = variant_mapping[comp]
                        
                        # Only keep allowed competitors
                        if comp in allowed_competitors:
                            filtered_competitors.append(comp)
                
                return filtered_competitors
            
            # Apply the extraction function to count individual competitor mentions
            competitor_mentions = []
            
            for comp_str in filtered_df['competitor_mentioned'].dropna():
                competitors = extract_competitors(comp_str)
                competitor_mentions.extend(competitors)
            
            # Count mentions of each competitor
            competitor_counts = pd.Series(competitor_mentions).value_counts()
            
            if len(competitor_counts) > 0:
                # Define how many top competitors to show
                top_n_to_show = min(8, len(competitor_counts))
                
                # Split into top competitors and others
                top_competitors = competitor_counts.head(top_n_to_show)
                other_competitors_count = competitor_counts[top_n_to_show:].sum()
                
                # Prepare data for plotting
                if other_competitors_count > 0:
                    display_data = pd.concat([
                        top_competitors,
                        pd.Series([other_competitors_count], index=["Others"])
                    ])
                else:
                    display_data = top_competitors
                
                # Create the plotly bar chart - capitalize competitor names for display
                display_data.index = [name.title() if name != "Others" else name for name in display_data.index]
                
                fig = px.bar(
                    x=display_data.index,
                    y=display_data.values,
                    labels={'x': 'Competitor', 'y': 'Number of Mentions'},
                    color=display_data.index,
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    height=500
                )
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Update layout
                fig.update_layout(
                    xaxis=dict(
                        tickangle=45
                    ),
                    yaxis=dict(
                        title="Number of Mentions"
                    ),
                    showlegend=False
                )
                
                # Add count labels
                fig.update_traces(
                    texttemplate='%{y:,}',
                    textposition='outside',
                    cliponaxis=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Topic-competitor association
                st.subheader("Topics Associated with Competitor Mentions")
                
                # Add a column to indicate if the review mentions an allowed competitor
                filtered_df['has_allowed_competitor'] = filtered_df['competitor_mentioned'].apply(
                    lambda x: len(extract_competitors(x)) > 0
                )
                
                # Calculate competitor mention rate for significant topics
                topic_competitor_data = []
                
                for topic in filtered_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                    # Get reviews with this topic
                    topic_reviews = filtered_df[filtered_df['topics'].str.contains(topic, na=False)]
                    
                    # Only include topics with enough reviews
                    if len(topic_reviews) >= 30:
                        competitor_pct = topic_reviews['has_allowed_competitor'].mean() * 100
                        
                        # Get top competitor for this topic
                        if competitor_pct > 0:
                            comp_reviews = topic_reviews[topic_reviews['has_allowed_competitor']]
                            top_competitor = None
                            
                            if len(comp_reviews) > 0:
                                comp_mentions = []
                                for comp_str in comp_reviews['competitor_mentioned'].dropna():
                                    comps = extract_competitors(comp_str)
                                    comp_mentions.extend(comps)
                                
                                if comp_mentions:
                                    top_competitor = pd.Series(comp_mentions).value_counts().index[0].title()
                            
                            topic_competitor_data.append({
                                'topic': topic,
                                'competitor_mention_rate': competitor_pct,
                                'review_count': len(topic_reviews),
                                'top_competitor': top_competitor
                            })
                
                # Convert to DataFrame and sort
                if topic_competitor_data:
                    topic_comp_df = pd.DataFrame(topic_competitor_data)
                    topic_comp_df = topic_comp_df.sort_values('competitor_mention_rate', ascending=False).head(15)
                    
                    # Create plotly bar chart
                    fig = px.bar(
                        topic_comp_df,
                        x='competitor_mention_rate',
                        y='topic',
                        orientation='h',
                        color='competitor_mention_rate',
                        color_continuous_scale='Oranges',
                        hover_data=['review_count', 'top_competitor'],
                        height=600
                    )
                    
                    # Apply consistent formatting
                    fig = format_plotly_fig(fig)
                    
                    # Add competitor labels
                    annotations = []
                    for i, row in enumerate(topic_comp_df.itertuples()):
                        if row.top_competitor:
                            annotations.append(
                                dict(
                                    x=row.competitor_mention_rate + 0.1,
                                    y=i,
                                    text=f"({row.top_competitor})",
                                    showarrow=False,
                                    font=dict(color="black", size=10)
                                )
                            )
                    
                    fig.update_layout(annotations=annotations)
                    
                    # Update layout
                    fig.update_layout(
                        xaxis=dict(
                            title="Percentage of Reviews Mentioning Competitors"
                        ),
                        yaxis=dict(
                            title=None,
                            autorange="reversed"  # Highest at top
                        ),
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Add explanation
                    st.markdown("""
                    <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                        <p><strong>💡 Insight:</strong> These topics are most frequently associated with competitor mentions in reviews. 
                        Topics with high competitor mention rates may indicate areas where users are comparing BMW's app with competitors' offerings.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No significant topic-competitor associations found")
            else:
                st.info("No competitor mentions found in the filtered data")
    else:
        st.info("Competitor data not available")

# TAB 6: FEATURE REQUESTS
with tabs[5]:
    # Use plain category header
    st.markdown('<div class="category-header">Feature Request Analysis</div>', unsafe_allow_html=True)
    
    if 'is_feature_request' in filtered_df.columns and 'topics' in filtered_df.columns:
        with st.container():
            st.subheader("Topics Most Associated with Feature Requests")
            
            # Calculate feature request prevalence for each topic
            topic_feature_requests = []
            
            for topic in filtered_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                # Get reviews with this topic
                topic_reviews = filtered_df[filtered_df['topics'].str.contains(topic, na=False)]
                
                # Only include topics with enough reviews
                if len(topic_reviews) >= 30:
                    # Calculate percentage of feature requests
                    if topic_reviews['is_feature_request'].dtype == 'object':
                        # If values are strings ('yes'/'no')
                        feature_count = (topic_reviews['is_feature_request'].str.lower() == 'yes').sum()
                        feature_pct = (feature_count / len(topic_reviews)) * 100
                    else:
                        # If values are boolean
                        feature_pct = topic_reviews['is_feature_request'].mean() * 100
                    
                    topic_feature_requests.append({
                        'topic': topic,
                        'feature_request_pct': feature_pct,
                        'review_count': len(topic_reviews)
                    })
            
            # Convert to DataFrame and sort
            if topic_feature_requests:
                fr_df = pd.DataFrame(topic_feature_requests)
                fr_df = fr_df.sort_values('feature_request_pct', ascending=False).head(15)
                
                # Create plotly bar chart
                fig = px.bar(
                    fr_df,
                    x='feature_request_pct',
                    y='topic',
                    orientation='h',
                    color='feature_request_pct',
                    color_continuous_scale='Purples',
                    hover_data=['review_count'],
                    height=600
                )
                
                # Apply consistent formatting
                fig = format_plotly_fig(fig)
                
                # Update layout
                fig.update_layout(
                    xaxis=dict(
                        title="Percentage of Reviews Containing Feature Requests",
                        range=[0, 100]
                    ),
                    yaxis=dict(
                        title=None,
                        autorange="reversed"  # Highest at top
                    ),
                    coloraxis_showscale=False
                )
                
                # Add count and percentage labels
                fig.update_traces(
                    texttemplate='%{x:.1f}%<br>(%{customdata[0]:,})',
                    textposition='outside',
                    hovertemplate='%{y}: %{x:.1f}% feature requests<br>Based on %{customdata[0]:,} reviews<extra></extra>'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add insights and recommendations section
                st.subheader("Insights & Recommendations")
                
                # Get the top 3 feature request topics
                top_topics = fr_df.head(3)['topic'].tolist()
                top_topics_str = ", ".join(f"'{t}'" for t in top_topics)
                
                st.markdown(f"""
                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                    <p><strong>📊 Key Insight:</strong> Topics with a high percentage of feature requests represent areas where users
                    are actively seeking improvements or new functionality in the MyBMW app.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No significant topic-feature request associations found")
                
        # Add Feature Request Timeline analysis
        with st.container():
            st.subheader("Feature Request Timeline")
            
            if 'is_feature_request' in filtered_df.columns and 'topics' in filtered_df.columns and 'appVersion' in filtered_df.columns:
                # Make sure we have version information
                if 'version_str' not in filtered_df.columns:
                    filtered_df['version_str'] = filtered_df['appVersion'].apply(
                        lambda x: re.match(r'(\d+\.\d+)', str(x)).group(1) if re.match(r'(\d+\.\d+)', str(x)) else np.nan
                    )
                
                # Convert version strings to numeric for sorting
                filtered_df['version_num'] = pd.to_numeric(filtered_df['version_str'], errors='coerce')
                
                # Drop rows with missing versions
                version_df = filtered_df.dropna(subset=['version_num'])
                
                if len(version_df) > 0:
                    # Get top feature request topics
                    feature_topics = []
                    
                    if topic_feature_requests:
                        # Use topics already identified in the analysis above
                        top_fr_topics = fr_df.head(5)['topic'].tolist()
                        feature_topics = top_fr_topics
                    else:
                        # Identify top feature request topics
                        for topic in version_df['topics'].dropna().str.split(',').explode().str.strip().unique():
                            # Get reviews with this topic
                            topic_reviews = version_df[version_df['topics'].str.contains(topic, na=False)]
                            
                            # Only include topics with enough reviews
                            if len(topic_reviews) >= 30:
                                # Calculate percentage of feature requests
                                if topic_reviews['is_feature_request'].dtype == 'object':
                                    # If values are strings ('yes'/'no')
                                    feature_count = (topic_reviews['is_feature_request'].str.lower() == 'yes').sum()
                                    feature_pct = (feature_count / len(topic_reviews)) * 100
                                else:
                                    # If values are boolean
                                    feature_pct = topic_reviews['is_feature_request'].mean() * 100
                                
                                if feature_pct >= 25:  # Only include topics with significant feature request rate
                                    feature_topics.append(topic)
                    
                    # Limit to top 5 topics
                    feature_topics = feature_topics[:5]
                    
                    if feature_topics:
                        # Create a DataFrame for the timeline analysis
                        timeline_data = []
                        
                        for topic in feature_topics:
                            # Get reviews for this topic
                            topic_reviews = version_df[version_df['topics'].str.contains(topic, na=False)]
                            
                            # Group by version and calculate feature request percentage
                            version_data = topic_reviews.groupby('version_str').apply(
                                lambda x: pd.Series({
                                    'total': len(x),
                                    'fr_count': (x['is_feature_request'].str.lower() == 'yes').sum() if x['is_feature_request'].dtype == 'object' else x['is_feature_request'].sum(),
                                    'fr_pct': ((x['is_feature_request'].str.lower() == 'yes').sum() / len(x) * 100) if x['is_feature_request'].dtype == 'object' else (x['is_feature_request'].mean() * 100)
                                })
                            )
                            
                            # Only include versions with enough data
                            version_data = version_data[version_data['total'] >= 10]
                            
                            # Convert to records
                            for version, row in version_data.iterrows():
                                timeline_data.append({
                                    'version': version,
                                    'topic': topic,
                                    'fr_pct': row['fr_pct'],
                                    'total': row['total'],
                                    'fr_count': row['fr_count']
                                })
                        
                        # Convert to DataFrame
                        if timeline_data:
                            timeline_df = pd.DataFrame(timeline_data)
                            
                            # Add version_num for sorting
                            timeline_df['version_num'] = pd.to_numeric(timeline_df['version'], errors='coerce')
                            timeline_df = timeline_df.sort_values('version_num')
                            
                            # Create a plotly line chart
                            fig = go.Figure()
                            
                            # Use a nice color palette
                            colors = px.colors.qualitative.Plotly[:len(feature_topics)]
                            line_styles = ['solid', 'dash', 'dot', 'dashdot', 'longdash']
                            
                            # Add a line for each topic
                            for i, topic in enumerate(feature_topics):
                                topic_data = timeline_df[timeline_df['topic'] == topic]
                                
                                if len(topic_data) >= 3:  # Only plot if we have enough data points
                                    fig.add_trace(go.Scatter(
                                        x=topic_data['version'],
                                        y=topic_data['fr_pct'],
                                        mode='lines+markers',
                                        name=topic,
                                        line=dict(
                                            color=colors[i % len(colors)],
                                            dash=line_styles[i % len(line_styles)],
                                            width=3
                                        ),
                                        marker=dict(size=8),
                                        customdata=np.stack((
                                            topic_data['total'],
                                            topic_data['fr_count']
                                        ), axis=-1),
                                        hovertemplate='%{y:.1f}% of reviews<br>%{customdata[1]} out of %{customdata[0]} reviews<extra></extra>'
                                    ))
                            
                            # Apply consistent formatting
                            fig = format_plotly_fig(fig)
                            
                            # Update layout
                            fig.update_layout(
                                xaxis=dict(
                                    title='App Version',
                                    tickangle=45,
                                    categoryorder='array',
                                    categoryarray=sorted(timeline_df['version'].unique(), key=lambda x: pd.to_numeric(x, errors='coerce'))
                                ),
                                yaxis=dict(
                                    title='Feature Request Percentage',
                                    range=[0, max(timeline_df['fr_pct']) * 1.1]
                                ),
                                legend=dict(
                                    title='Topics',
                                    orientation='h',
                                    yanchor='bottom',
                                    y=1.02,
                                    xanchor='right',
                                    x=1
                                ),
                                height=500
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Identify topics with significant increases
                            growing_requests = []
                            
                            for topic in feature_topics:
                                topic_data = timeline_df[timeline_df['topic'] == topic]
                                
                                if len(topic_data) >= 3:
                                    # Calculate slope using simple linear regression
                                    x = np.arange(len(topic_data))
                                    y = topic_data['fr_pct'].values
                                    slope, _ = np.polyfit(x, y, 1)
                                    
                                    # Identify significant positive slopes
                                    if slope > 1:  # More than 1 percentage point increase per version on average
                                        earliest = topic_data.iloc[0]['fr_pct']
                                        latest = topic_data.iloc[-1]['fr_pct']
                                        percent_increase = ((latest - earliest) / earliest) * 100 if earliest > 0 else 0
                                        
                                        growing_requests.append({
                                            'topic': topic,
                                            'slope': slope,
                                            'percent_increase': percent_increase,
                                            'earliest': earliest,
                                            'latest': latest,
                                            'versions': len(topic_data),
                                            'earliest_version': topic_data.iloc[0]['version'],
                                            'latest_version': topic_data.iloc[-1]['version']
                                        })
                            
                            # Add insight based on trending feature requests
                            if growing_requests:
                                # Sort by percent increase
                                growing_requests.sort(key=lambda x: x['percent_increase'], reverse=True)
                                top_growing = growing_requests[0]
                                
                                st.markdown(f"""
                                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                                    <p><strong>💡 Insight:</strong> Feature requests for <strong>{top_growing['topic']}</strong> have increased by <strong>{top_growing['percent_increase']:.1f}%</strong> from version {top_growing['earliest_version']} to {top_growing['latest_version']} (from {top_growing['earliest']:.1f}% to {top_growing['latest']:.1f}%), suggesting growing user demand for this functionality.</p>
                                    <p>Rapidly growing feature request trends often indicate emerging user needs or competitive features that users are increasingly expecting in the app.</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div style="background-color: var(--card-bg-color); padding: 15px; border-radius: 5px; margin-top: 20px; border: 1px solid var(--card-border-color);">
                                    <p><strong>💡 Insight:</strong> Feature request patterns are relatively stable across versions, suggesting consistent user expectations rather than rapidly emerging new demands.</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("Not enough version data for feature request timeline analysis")
                    else:
                        st.info("No significant feature request topics identified")
                else:
                    st.info("Not enough version data available for timeline analysis")
            else:
                st.info("Feature request, topic, or app version data not available for timeline analysis")
    else:
        st.info("Feature request data not available")

# Add a section for data download with plain header
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Export Data</div>', unsafe_allow_html=True)

# Create columns for export options
col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.subheader("Download Filtered Data")
        st.markdown("Export the current filtered dataset as CSV for further analysis.")
        
        # Allow downloading the filtered dataset
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='filtered_bmw_reviews.csv',
            mime='text/csv',
        )

with col2:
    with st.container():
        st.subheader("Filter Summary")
        
        # Create a summary of current filters
        st.markdown("### Current Filters Applied")
        
        filter_info = [
            f"**Total Reviews**: {len(filtered_df):,} out of {len(df):,} ({len(filtered_df)/len(df)*100:.1f}%)"
        ]
        
        if 'date' in df.columns and len(date_range) == 2:
            filter_info.append(f"**Date Range**: {date_range[0]} to {date_range[1]}")
        
        if 'language' in df.columns and selected_language != 'All':
            filter_info.append(f"**Language**: {selected_language}")
        
        if 'score' in df.columns:
            filter_info.append(f"**Rating Range**: {selected_ratings[0]} to {selected_ratings[1]} stars")
        
        if 'appVersion' in df.columns and selected_version != 'All':
            filter_info.append(f"**App Version**: {selected_version}")
        
        for info in filter_info:
            st.markdown(info)

# Add footer
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>MyBMW App Review Text Mining Dashboard | Created with Streamlit</p>
    <p>This dashboard provides insights derived from text mining and sentiment analysis of user reviews.</p>
</div>
""", unsafe_allow_html=True)