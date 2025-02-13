# data_processing.py
import pandas as pd
import subprocess
from tqdm import tqdm
import matplotlib.pyplot as plt
from google_play_scraper import Sort, reviews
from itertools import combinations
import networkx as nx

# ================================
# Parameters and Prompt Templates
# ================================
APP_ID = "de.bmw.connected.mobile20.row"
OLLAMA_MODEL_NAME = "llama3.2:3b-instruct-fp16"

# Sentiment classification prompt template
OLLAMA_PROMPT_TEMPLATE = """You are a sentiment classifier. Classify the sentiment of the following text as Positive, Negative, or Neutral. Do not add any additional information.
Text: "{review_text}"
Answer:
"""

# ================================
# 1. Fetch Reviews from Google Play Store
# ================================
def fetch_reviews():
    # List of languages (code, label)
    languages = [
        ('en', 'English'),
        ('de', 'German'),
        ('fr', 'French'),
        ('it', 'Italian'),
        ('es', 'Spanish'),
        ('nl', 'Dutch'),
        ('sv', 'Swedish'),
        ('da', 'Danish'),
        ('no', 'Norwegian'),
        ('fi', 'Finnish'),
        ('pl', 'Polish'),
        ('cs', 'Czech'),
        ('pt', 'Portuguese'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ar', 'Arabic'),
        ('tr', 'Turkish'),
        ('ru', 'Russian'),
        ('he', 'Hebrew'),
        ('th', 'Thai'),
        ('vi', 'Vietnamese'),
        ('hi', 'Hindi'),
        ('el', 'Greek'),
        ('hu', 'Hungarian'),
        ('ro', 'Romanian'),
        ('sk', 'Slovak'),
        ('bg', 'Bulgarian'),
        ('hr', 'Croatian'),
        ('sr', 'Serbian'),
        ('uk', 'Ukrainian'),
        ('id', 'Indonesian'),
        ('ms', 'Malay'),
        ('fa', 'Persian'),
        ('ur', 'Urdu'),
        ('bn', 'Bengali'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('ml', 'Malayalam'),
        ('et', 'Estonian'),
        ('lv', 'Latvian'),
        ('lt', 'Lithuanian'),
        ('sl', 'Slovenian')
    ]

    all_reviews = []
    for lang_code, lang_label in languages:
        continuation_token = None
        prev_length = len(all_reviews)
        while True:
            result, continuation_token = reviews(
                APP_ID,
                lang=lang_code,
                sort=Sort.NEWEST,
                count=100,
                continuation_token=continuation_token
            )
            # Add language label to each review
            for review in result:
                review['language'] = lang_label
            all_reviews.extend(result)
            current_length = len(all_reviews)
            if not continuation_token or current_length - prev_length < 100:
                break
            prev_length = current_length

    df = pd.DataFrame(all_reviews)
    return df

# ================================
# 2. Sample Reviews
# ================================
def sample_reviews(df, n=500, random_state=42):
    return df.sample(n=n, random_state=random_state)

# ================================
# 3. Translate Non-English Reviews
# ================================
def translate_text(text, source_lang):
    prompt = f"""You are a translator. Translate the following {source_lang} text to English.
Only provide the translation, no additional information.
Text: "{text}"
Translation:"""
    process = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL_NAME],
        input=prompt,
        text=True,
        capture_output=True
    )
    return process.stdout.strip()

def translate_reviews(df):
    # Create a new column 'content_english' as a copy of 'content'
    df['content_english'] = df['content']
    non_english_indices = df[df['language'] != 'English'].index
    for idx in tqdm(non_english_indices, desc="Translating reviews"):
        original_text = df.loc[idx, 'content']
        source_lang = df.loc[idx, 'language']
        translated_text = translate_text(original_text, source_lang)
        df.loc[idx, 'content_english'] = translated_text
    return df

# ================================
# 4. Sentiment Analysis
# ================================
def get_sentiment_from_ollama(text):
    # Use the English translation for non-English reviews
    text_to_analyze = text['content_english'] if isinstance(text, pd.Series) else text
    prompt = OLLAMA_PROMPT_TEMPLATE.format(review_text=text_to_analyze)
    process = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL_NAME],
        input=prompt,
        text=True,
        capture_output=True
    )
    return process.stdout.strip()

def run_sentiment_analysis(df):
    sentiments = []
    total_reviews = len(df)
    for idx, row in tqdm(df.iterrows(), total=total_reviews, desc="Analyzing Sentiment"):
        sentiment_label = get_sentiment_from_ollama(row)
        sentiments.append(sentiment_label)
    df['sentiment'] = sentiments
    return df

# ================================
# 5. Topic Labeling
# ================================
def label_review_topics(text):
    REVIEW_TOPICS = """
1. UI/UX:
   - User interface, app design, ease of use, navigation, overall visual appeal.
2. Performance:
   - App speed, crashes, bugs, stability, battery drain.
3. Connectivity:
   - Connection issues, Bluetooth, server problems, integration with external devices.
4. Authentication:
   - Login issues, account problems, multi-factor authentication, session timeouts.
5. Vehicle Status:
   - Battery, fuel, location, diagnostics.
6. Remote Controls:
   - Lock/unlock, climate control, remote start.
7. Trip Planning:
   - Route optimization, scheduling, and related features.
8. Charging Management:
   - Charging status, locating charging stations, scheduling.
9. Map/Navigation:
   - Maps functionality, route planning, GPS accuracy, alternative route suggestions.
10. Mobile Features:
   - Widgets, notifications, mobile-specific interactions, quick-access features.
11. Data & Privacy:
   - Data handling, privacy concerns, data sharing, security practices.
12. Updates:
   - App updates, version issues, patch notes, update-related bugs.
13. Feature Requests:
    - Desired new functionality, user suggestions for enhancements.
14. Customer Support:
    - Support experience, response time, issue resolution, helpdesk effectiveness.
15. Connected Store:
    - In-app store experience, product browsing, payment process, promotional offers, purchase issues, ease of transaction.
16. BMW Digital Premium:
    - Subscription service experience, access to premium features, content quality, subscription pricing, management of subscription settings.
"""
    prompt = f"""You are a review topic classifier. Given the following review, identify ALL relevant topics it discusses.
Use ONLY the topics from this list:
{REVIEW_TOPICS}

Review text: "{text}"

Output the topics as a simple comma-separated list, with no additional text or explanations.
If you are not sure about the topics, output the word "Other".
"""
    process = subprocess.run(
        ["ollama", "run", OLLAMA_MODEL_NAME],
        input=prompt,
        text=True,
        capture_output=True
    )
    return process.stdout.strip()

def run_topic_labeling(df):
    topics = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing Topics"):
        review_topics = label_review_topics(row['content_english'])
        topics.append(review_topics)
    df['topics'] = topics
    return df

# ================================
# 6. Analysis Helpers
# ================================
def compute_sentiment_counts(df):
    return df['sentiment'].value_counts()

def compute_topic_counts(df):
    all_topics = []
    for topic_list in df['topics']:
        topics = [t.strip() for t in topic_list.split(',')]
        all_topics.extend(topics)
    return pd.Series(all_topics).value_counts()

# (Additional analysis functions such as time-based analysis,
# co-occurrence analysis, etc., can be added here as needed.)

# ================================
# 7. Main Data Processing Pipeline
# ================================
def process_data():
    # Fetch reviews from the Play Store
    df = fetch_reviews()
    print(f"Fetched {len(df)} reviews")
    
    # Sample a subset for analysis
    df_sampled = sample_reviews(df, n=500)
    print(f"Sampled {len(df_sampled)} reviews for analysis")
    
    # Translate non-English reviews
    df_translated = translate_reviews(df_sampled)
    
    # Run sentiment analysis
    df_with_sentiment = run_sentiment_analysis(df_translated)
    
    # Run topic labeling
    df_final = run_topic_labeling(df_with_sentiment)
    
    # Ensure the time stamp column is in datetime format
    if 'at' in df_final.columns:
        df_final['at'] = pd.to_datetime(df_final['at'])
    else:
        print("Warning: 'at' column (review timestamp) not found.")
    
    return df_final

# ================================
# Standalone Execution
# ================================
if __name__ == "__main__":
    df_processed = process_data()
    print("\nProcessed DataFrame:")
    print(df_processed.head())
    
    sentiment_counts = compute_sentiment_counts(df_processed)
    print("\nSentiment Distribution:")
    print(sentiment_counts)
    
    topic_counts = compute_topic_counts(df_processed)
    print("\nTopic Distribution:")
    print(topic_counts)
    
    # (Optional: call any analysis plotting functions here.)