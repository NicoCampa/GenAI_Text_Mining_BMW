import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Import functions from your processing module
from data_processing import process_data, compute_sentiment_counts, compute_topic_counts

# Set page configuration
st.set_page_config(page_title="BMW App Reviews Analysis", layout="wide")

# Title and description
st.title("BMW Connected App User Reviews Analysis")
st.markdown("Analysis of user reviews from the BMW Connected mobile application")

# Define the cache file path
CACHE_FILE = "cached_data.pkl"

@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists(CACHE_FILE):
        df = pd.read_pickle(CACHE_FILE)
        st.info("Loaded data from cached file.")
    else:
        df = process_data()
        df.to_pickle(CACHE_FILE)
        st.info("Processed new data and cached to file.")
    return df

# Optional: Allow the user to clear the cache for a fresh processing run.
if st.button("Clear Cache & Refresh Data"):
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    st.rerun()

# Load the data (using cache if available)
df2 = load_data()

# =============================================================================
# Compute Additional Metrics for Visualization
# =============================================================================
# Sentiment counts
sentiment_counts = compute_sentiment_counts(df2)

# Define color mapping for sentiments
sentiment_color_dict = {"Positive": "green", "Negative": "red", "Neutral": "gray"}

# Ratings distribution (assumes column 'score' exists)
rating_counts = df2['score'].value_counts().sort_index()

# Topic counts (computed from your topic labeling)
topic_counts = compute_topic_counts(df2)

# Build a topic-sentiment pivot table.
topic_sentiment_data = []
for _, row in df2.iterrows():
    topics = [t.strip() for t in row['topics'].split(',')]
    for topic in topics:
        topic_sentiment_data.append({
            'topic': topic,
            'sentiment': row['sentiment']
        })
topic_sentiment_df = pd.DataFrame(topic_sentiment_data)
topic_sentiment_grouped = pd.crosstab(topic_sentiment_df['topic'], topic_sentiment_df['sentiment'])

# Reviews over time (assuming the processed data has a datetime column "at")
if 'at' in df2.columns:
    reviews_over_time = df2.set_index('at').resample('M').size()
else:
    reviews_over_time = pd.Series(dtype=int)
    st.warning("The time column 'at' was not found in the data.")

# =============================================================================
# Layout the Dashboard
# =============================================================================

# Two-column layout for overall sentiment and ratings
col1, col2 = st.columns(2)

with col1:
    st.subheader("Overall Sentiment Distribution")
    sentiment_fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        color=sentiment_counts.index,
        color_discrete_map=sentiment_color_dict,
        title="Distribution of Review Sentiments"
    )
    st.plotly_chart(sentiment_fig)

with col2:
    st.subheader("Rating Distribution")
    rating_fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        title="Distribution of Star Ratings",
        labels={'x': 'Star Rating', 'y': 'Count'}
    )
    st.plotly_chart(rating_fig)

# Topic Analysis Section
st.subheader("Topic Analysis")
col3, col4 = st.columns(2)

with col3:
    # Display the top 10 topics
    top_topics = topic_counts.head(10)
    topics_fig = px.bar(
        x=top_topics.index,
        y=top_topics.values,
        title="Top 10 Topics Mentioned in Reviews",
        labels={'x': 'Topic', 'y': 'Count'}
    )
    st.plotly_chart(topics_fig)

with col4:
    # Topic-Sentiment Relationship: Stacked horizontal bar chart
    topic_sentiment_fig = go.Figure(data=[
        go.Bar(name='Positive', y=topic_sentiment_grouped.index[:10],
               x=topic_sentiment_grouped['Positive'][:10], orientation='h'),
        go.Bar(name='Negative', y=topic_sentiment_grouped.index[:10],
               x=topic_sentiment_grouped['Negative'][:10], orientation='h'),
        go.Bar(name='Neutral', y=topic_sentiment_grouped.index[:10],
               x=topic_sentiment_grouped['Neutral'][:10], orientation='h')
    ])
    topic_sentiment_fig.update_layout(
        barmode='stack',
        title="Topic-Sentiment Distribution (Top 10 Topics)",
        xaxis_title="Count",
        yaxis_title="Topic"
    )
    st.plotly_chart(topic_sentiment_fig)

# Language Distribution
st.subheader("Review Language Distribution")
lang_dist = df2['language'].value_counts().head(10)
lang_fig = px.pie(
    values=lang_dist.values,
    names=lang_dist.index,
    title="Distribution of Review Languages (Top 10)"
)
st.plotly_chart(lang_fig)

# Time Series Analysis: Reviews over time
st.subheader("Reviews Over Time")
time_fig = px.line(
    x=reviews_over_time.index,
    y=reviews_over_time.values,
    title="Number of Reviews Over Time",
    labels={'x': 'Date', 'y': 'Number of Reviews'}
)
st.plotly_chart(time_fig)

# Summary Statistics
st.subheader("Summary Statistics")
col5, col6, col7 = st.columns(3)

with col5:
    st.metric("Total Reviews", len(df2))
    
with col6:
    avg_rating = df2['score'].mean() if 'score' in df2.columns else 0
    st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
    
with col7:
    if 'Positive' in sentiment_counts.index:
        positive_pct = (sentiment_counts['Positive'] / len(df2)) * 100
        st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
    else:
        st.metric("Positive Sentiment", "N/A")