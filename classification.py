# ======================================
# BMW App Review Analysis - Single-Task Classification
# ======================================
import os
import glob
import time
import subprocess
import pandas as pd
import json
import logging
from tqdm import tqdm
from typing import Dict, List, Optional, Union
import traceback
from datetime import datetime

# Ollama model
ollama_model_name = "gemma3:12b"

# Create organized folder structure
BASE_DIR = "bmw_app_analysis"
CHECKPOINT_DIR = os.path.join(BASE_DIR, "checkpoints")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create all directories
for directory in [BASE_DIR, CHECKPOINT_DIR, RESULTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# File to track progress
PROGRESS_FILE = os.path.join(BASE_DIR, "analysis_progress.json")

# Ensure display is imported for notebooks
try:
    from IPython.display import display
except ImportError:
    display = print  # Fallback for non-notebook environments

# Set up logging
log_file = os.path.join(LOGS_DIR, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console
    ]
)

# Utility function to run Ollama (reused from original code)
def run_ollama(prompt: str, model_name: str) -> str:
    """Execute Ollama model with the provided prompt."""
    try:
        process = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            encoding='utf-8'
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."
        logging.error(f"Ollama command failed with exit code {e.returncode}. Stderr: {stderr_output}")
        return ""
    except Exception as e:
        logging.error(f"An unexpected error occurred running Ollama: {e}")
        return ""

# ======================================
# Individual Classification Functions
# ======================================

def classify_sentiment(review_text: str, model_name: str) -> str:
    """
    Classify the sentiment of a review text as positive, negative, or neutral.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "positive", "negative", or "neutral" (lowercase)
    """
    if not review_text or not isinstance(review_text, str):
        return "neutral"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Classify the sentiment of this review:

"{review_text}"

CLASSIFICATION TASK:
Determine if the sentiment is positive, negative, or neutral.

DETAILED GUIDELINES:
- Positive: 
  * User explicitly expresses satisfaction, appreciation, praise
  * Uses positive adjectives (great, excellent, amazing, love)
  * Shows enthusiasm about features or performance
  * Reports problems being fixed or improvements made
  * Explicitly recommends the app to others
  * Contains predominantly positive language despite minor issues

- Negative:
  * User explicitly expresses dissatisfaction, frustration, anger
  * Reports bugs, crashes, failures, or malfunctions
  * Uses negative adjectives (terrible, awful, useless, poor)
  * States the app doesn't work as expected or advertised
  * User had to find workarounds for basic functionality
  * Contains predominantly critical language despite minor praise

- Neutral:
  * Balance of positive and negative points with neither dominating
  * Factual descriptions without emotional language
  * Questions about functionality without clear satisfaction/dissatisfaction
  * Suggestions for improvements without expressing frustration
  * Simple factual statements about the app's functions
  * Too vague to determine sentiment clearly
 
IMPORTANT DECISION RULES:
- If review mentions both positives and negatives, focus on:
  1. The strongest emotional language (which sentiment has stronger expressions?)
  2. The most recent experience (latest update/version)
  3. Core functionality issues outweigh minor aesthetic praise
  4. Essential features working outweighs minor inconveniences
- Very short reviews with just "good" = positive, "bad" = negative, "ok" = neutral
- Sarcasm should be interpreted for the underlying sentiment ("Great, another crash" = negative)
- If review is exceptionally ambiguous, default to "neutral"

EXAMPLES:
1. "Great app, works perfectly every time!" → positive
2. "App keeps crashing when I try to check my car status." → negative
3. "The app is okay but could use some improvements." → neutral
4. "Used to crash constantly but recent update fixed most issues." → positive (most recent experience)
5. "Nice design but completely useless as it fails to connect to my car." → negative (core functionality issue)
6. "The app has some bugs but generally works well enough for what I need." → neutral (balanced)
7. "I'm impressed with the range of features, though it occasionally lags." → positive (stronger positive than negative)
8. "Loading times are frustratingly slow but at least it doesn't crash anymore." → neutral (balanced positives/negatives)

RESPONSE FORMAT:
Respond with ONLY ONE WORD: positive, negative, or neutral (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        valid_sentiments = ["positive", "negative", "neutral"]
        if response in valid_sentiments:
            return response
        
        # Handle potential extra text by checking for valid sentiment words
        for sentiment in valid_sentiments:
            if sentiment in response:
                logging.warning(f"Extracted '{sentiment}' from response: '{response}'")
                return sentiment
                
        # Default if response is invalid
        logging.warning(f"Invalid sentiment response: '{response}'. Defaulting to 'neutral'")
        return "neutral"
    except Exception as e:
        logging.error(f"Sentiment classification failed: {str(e)}")
        return "neutral"


def classify_topics(review_text: str, model_name: str) -> str:
    """
    Identify the relevant topics in a review from a predefined list.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: Comma-separated topic list, or "other"
    """
    if not review_text or not isinstance(review_text, str):
        return "other"
    
    # Valid topics list - used for verification
    valid_topics = [
        "ui/ux", "performance", "connectivity", "authentication", 
        "vehicle status", "remote controls", "trip planning", 
        "charging management", "map/navigation", "mobile features", 
        "data & privacy", "updates", "customer support",
        "connected store", "bmw digital premium", "digital key/mobile key",
        "vehicle configuration & personalization", "multimedia integration",
        "smartphone integration", "service & maintenance", "parking solutions",
        "voice assistant", "my garage/vehicle management", "localization & language",
        "bmw connected ecosystem", "ev-specific features", "notification management",
        "usage statistics", "tutorial/help section", "other"
    ]
    
    # BMW review topics list (abbreviated for prompt space)
    topics_list = """
    1. ui/ux - design, usability, navigation, visual appeal
    2. performance - speed, crashes, bugs, stability, battery drain
    3. connectivity - connection issues, bluetooth, server integration
    4. authentication - login, account issues, multi-factor
    5. vehicle status - battery/fuel level, location, diagnostics
    6. remote controls - lock/unlock, climate, remote start
    7. trip planning - route optimization, scheduling
    8. charging management - status, stations, scheduling
    9. map/navigation - maps, route planning, gps accuracy
    10. mobile features - widgets, notifications, interactions
    11. data & privacy - data handling, security concerns
    12. updates - app updates, version issues, bugs
    13. customer support - support experience, response time
    14. connected store - in-app store, purchases, products
    15. bmw digital premium - subscription services, premium features
    16. digital key/mobile key - phone as key, sharing, access
    17. vehicle configuration & personalization - profiles, settings
    18. multimedia integration - music control, media streaming
    19. smartphone integration - carplay, android auto
    20. service & maintenance - scheduling, alerts, history
    21. parking solutions - location, payments, availability
    22. voice assistant - voice commands, assistant functionality
    23. my garage/vehicle management - multiple vehicles, profiles
    24. localization & language - translations, regional features
    25. bmw connected ecosystem - integration with other bmw services
    26. ev-specific features - range, charging, battery features
    27. notification management - app alerts, push notifications, alert settings
    28. usage statistics - mileage tracking, fuel/energy consumption, driving history
    29. tutorial/help section - in-app guidance, manuals, feature explanations
    """
    
    prompt = f"""You are an expert at analyzing BMW app reviews. Identify the main topics discussed in this review:

"{review_text}"

CLASSIFICATION TASK:
Identify 1-5 most relevant topics from this list:
{topics_list}

STRICT RESPONSE RULES:
1. RESPOND ONLY with topic names from the list, separated by commas
2. DO NOT write any explanations, introductions, or reasoning
3. DO NOT write complete sentences
4. USE ONLY the exact topic names listed above
5. If no topics apply, just respond with "other"
6. Use lowercase only

EXAMPLES:
Review: "The app crashes every time I try to check my battery level"
Valid response: performance, vehicle status

Review: "Love the new design! Very easy to use."
Valid response: ui/ux

Review: "Can't connect to my car. Bluetooth always fails."
Valid response: connectivity

Review: "ok"
Valid response: other

Review: "Would be nice if it had a way to schedule charging on my i4"
Valid response: feature requests, charging management, ev-specific features

IMPORTANT: Your entire response must be ONLY the topic names, nothing else. No explanations or additional text allowed.
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Clean basic things like quotes and periods
        response = response.replace('"', '').replace("'", '').replace(".", "").replace("!", "").replace("?", "")
        
        # VALIDATION: Split by commas and validate each topic
        if not response or len(response) > 200:  # Avoid extremely long responses
            return "other"
            
        # Split the response
        topics = [t.strip() for t in response.split(',')]
        
        # Filter to keep only valid topics
        valid_results = []
        for topic in topics:
            if topic in valid_topics:
                valid_results.append(topic)
            # Skip invalid topics
        
        # If no valid topics remain, return "other"
        if not valid_results:
            return "other"
            
        # Return validated topics
        return ", ".join(valid_results)
        
    except Exception as e:
        logging.error(f"Topic classification failed: {str(e)}")
        return "other"

def classify_vehicle_type(review_text: str, model_name: str) -> str:
    """
    Determine if the review refers to an electric/hybrid vehicle, combustion engine, or is unclear.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "ev_hybrid", "combustion", or "unclear"
    """
    if not review_text or not isinstance(review_text, str):
        return "unclear"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Determine what type of vehicle the user has based on this review:

"{review_text}"

CLASSIFICATION TASK:
Determine if the user has an electric/hybrid vehicle (BMW EV or PHEV), a combustion engine vehicle, or if it's unclear.

GUIDELINES:
- Classify as "ev_hybrid" if the review mentions:
  * Charging or battery level (in %, kWh)
  * Electric range or range anxiety
  * Charging stations or charging schedule
  * Preconditioning related to battery (warming up the battery)
  * Regenerative braking
  * Any BMW EV or hybrid model names (i3, i4, i5, i7, iX, 330e, 530e, X5 45e/50e)
  * Explicitly says "electric" or "EV" or "plug-in hybrid"

- Classify as "combustion" if the review mentions:
  * Fuel level, gas, petrol, diesel explicitly
  * Engine sounds or non-electric engine characteristics
  * MPG, l/100km in context of fuel
  * Explicitly mentions combustion-only models (e.g., "my M3", "my 330i")
  * Refers to refueling or gas stations

- Classify as "unclear" if:
  * No specific vehicle type indicators are present
  * Only mentions general features that apply to both types
  * Only mentions "my BMW" with no specific model
  * Cannot determine confidently from the text

EXAMPLES:
1. "App shows my battery at 80% but my actual i4 shows 75%" → ev_hybrid
2. "I can't find where to set up my charging schedule" → ev_hybrid
3. "Fuel gauge is incorrect, shows half tank when I just filled up my X3" → combustion
4. "Can't connect to my car at all" → unclear
5. "Love that I can precondition the cabin" → unclear (both vehicle types have this)
6. "Shows range but not how much gas is left" → combustion
7. "The range estimation is way off on my 330e" → ev_hybrid
8. "Where is the button to lock my car?" → unclear

RESPONSE FORMAT:
Respond with ONLY ONE WORD: ev_hybrid, combustion, or unclear (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        valid_types = ["ev_hybrid", "combustion", "unclear"]
        if response in valid_types:
            return response
        
        # Handle potential extra text by checking for valid vehicle type words
        for vehicle_type in valid_types:
            if vehicle_type in response:
                logging.warning(f"Extracted '{vehicle_type}' from response: '{response}'")
                return vehicle_type
                
        # Default if response is invalid
        logging.warning(f"Invalid vehicle type response: '{response}'. Defaulting to 'unclear'")
        return "unclear"
    except Exception as e:
        logging.error(f"Vehicle type classification failed: {str(e)}")
        return "unclear"


def classify_user_experience(review_text: str, model_name: str) -> str:
    """
    Determine if the user is new to the app, an experienced user, or if it's unclear.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "new_user", "experienced_user", or "unclear"
    """
    if not review_text or not isinstance(review_text, str):
        return "unclear"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Determine how experienced the user is with the BMW app based on this review:

"{review_text}"

CLASSIFICATION TASK:
Classify whether the user is new to the app, experienced with it, or if it's unclear.

GUIDELINES:
- Classify as "new_user" if the review mentions:
  * Just downloaded or installed
  * First impressions
  * Just got the car
  * Recently purchased
  * Setting up for the first time
  * Initial experience
  * New to BMW or the app

- Classify as "experienced_user" if the review mentions:
  * Using the app for a period of time (months/years)
  * References to previous versions of the app
  * Comparisons to how the app used to work
  * Updates changing functionality they're familiar with
  * Being a long-time BMW owner
  * Historical perspective on app changes

- Classify as "unclear" if:
  * No time references or experience level indicators
  * Cannot determine confidently from the text
  * Only gives current impression without historical context

EXAMPLES:
1. "Just got my new BMW and can't figure out how to set up the app" → new_user
2. "Been using this app for 3 years and the latest update broke everything" → experienced_user
3. "The app keeps crashing when I check vehicle status" → unclear
4. "The old version was much better, this redesign is terrible" → experienced_user
5. "First day using it and I'm already impressed with the features" → new_user
6. "This app sucks" → unclear

RESPONSE FORMAT:
Respond with ONLY ONE WORD: new_user, experienced_user, or unclear (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        valid_types = ["new_user", "experienced_user", "unclear"]
        if response in valid_types:
            return response
        
        # Handle common variations
        if "new" in response:
            return "new_user"
        if "experienced" in response or "experience" in response:
            return "experienced_user"
                
        # Default if response is invalid
        logging.warning(f"Invalid user experience response: '{response}'. Defaulting to 'unclear'")
        return "unclear"
    except Exception as e:
        logging.error(f"User experience classification failed: {str(e)}")
        return "unclear"


def classify_usage_profile(review_text: str, model_name: str) -> str:
    """
    Determine if the user is a power user, casual user, or if it's unclear.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "power_user", "casual_user", or "unclear"
    """
    if not review_text or not isinstance(review_text, str):
        return "unclear"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Determine the user's usage pattern based on this review:

"{review_text}"

CLASSIFICATION TASK:
Classify whether the user is a power user who uses advanced features, a casual user who uses basic features, or if it's unclear.

GUIDELINES:
- Classify as "power_user" if the review mentions:
  * Multiple advanced features (trip planning, automation, custom settings)
  * Integration with smart home or other services
  * Technical details about functionality
  * Complex use cases beyond basic car controls
  * Digital key plus or advanced features
  * Detailed technical feedback suggesting deep engagement
  * Regular/daily use of multiple features

- Classify as "casual_user" if the review mentions:
  * Only basic features (lock/unlock, climate control, basic status)
  * Simple use cases like checking fuel/charge or location
  * General non-technical feedback
  * Occasional or infrequent use
  * Focuses on core simple functions only

- Classify as "unclear" if:
  * No specific features or usage patterns mentioned
  * Cannot determine usage depth from the text
  * General comments that don't indicate how they use the app

EXAMPLES:
1. "Can't get the digital key to work with my smart home automation" → power_user
2. "I just use it to check my fuel level and lock the doors occasionally" → casual_user
3. "App keeps crashing" → unclear
4. "Love how I can set up charging schedules and have the climate start automatically based on my calendar" → power_user
5. "It's annoying that I have to restart it every time I want to check where I parked" → casual_user
6. "Decent app but needs improvement" → unclear

RESPONSE FORMAT:
Respond with ONLY ONE WORD: power_user, casual_user, or unclear (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        valid_types = ["power_user", "casual_user", "unclear"]
        if response in valid_types:
            return response
        
        # Handle common variations
        if "power" in response:
            return "power_user"
        if "casual" in response:
            return "casual_user"
                
        # Default if response is invalid
        logging.warning(f"Invalid usage profile response: '{response}'. Defaulting to 'unclear'")
        return "unclear"
    except Exception as e:
        logging.error(f"Usage profile classification failed: {str(e)}")
        return "unclear"


def classify_pain_point(review_text: str, model_name: str) -> str:
    """
    Determine if the review mentions a pain point (yes/no).
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "yes" or "no"
    """
    if not review_text or not isinstance(review_text, str):
        return "no"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Determine if this review mentions any pain points:

"{review_text}"

CLASSIFICATION TASK:
Determine if the user mentions any pain points, issues, or problems with the app.

GUIDELINES:
Classify as "yes" if the review mentions:
- Crashes, bugs, glitches, or technical issues
- Features not working as expected
- Frustration or difficulty using the app
- Complaints about design or performance
- Connection failures or syncing problems
- Missing expected functionality
- Errors or unexpected behavior
- Battery drain or other resource issues
- Anything the user clearly finds problematic

Classify as "no" if:
- The review is generally positive
- No specific issues or problems are mentioned
- The user is only making general comments or asking questions
- The review only contains feature requests without complaints

EXAMPLES:
1. "App keeps crashing when I try to check status" → yes
2. "Works great every time!" → no
3. "Why is it so hard to find the charging settings?" → yes
4. "Would be nice if you could add a widget" → no (feature request without complaint)
5. "Can't connect to my car half the time. Very frustrating!" → yes
6. "Just got the app. Looking forward to using it." → no

RESPONSE FORMAT:
Respond with ONLY ONE WORD: yes or no (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        if response in ["yes", "no"]:
            return response
            
        # Handle potential extra text
        if "yes" in response:
            return "yes"
        if "no" in response:
            return "no"
                
        # Default if response is invalid
        logging.warning(f"Invalid pain point response: '{response}'. Defaulting to 'no'")
        return "no"
    except Exception as e:
        logging.error(f"Pain point classification failed: {str(e)}")
        return "no"


def classify_feature_request(review_text: str, model_name: str) -> str:
    """
    Determine if the review contains a feature request (yes/no).
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        str: "yes" or "no"
    """
    if not review_text or not isinstance(review_text, str):
        return "no"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Determine if this review contains a feature request:

"{review_text}"

CLASSIFICATION TASK:
Determine if the user is explicitly asking for or suggesting new features or improvements.

GUIDELINES:
Classify as "yes" if the review:
- Explicitly asks for a new feature to be added
- Suggests improvements to existing functionality
- Uses phrases like "would be nice if", "wish it had", "please add"
- Compares to missing features in other apps they want implemented
- Describes functionality they want but that doesn't exist yet
- Makes specific suggestions for changes or additions
- Expresses desire for missing capabilities

Classify as "no" if:
- The review doesn't suggest any improvements or new features
- The user is only reporting bugs or issues with existing features
- The user is only describing current functionality
- The review only contains complaints without suggesting solutions

EXAMPLES:
1. "Would be great if you could add Apple Watch support" → yes
2. "The app keeps crashing" → no
3. "Please add the ability to schedule charging" → yes
4. "Why can't I see my trip history like in the Mercedes app?" → yes
5. "The UI is terrible and confusing" → no (complaint without suggestion)
6. "You should include a way to share my location with family members" → yes
7. "I wish there was a widget for quick access" → yes
8. "Works great" → no

RESPONSE FORMAT:
Respond with ONLY ONE WORD: yes or no (lowercase, no punctuation).
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Validate response
        if response in ["yes", "no"]:
            return response
            
        # Handle potential extra text
        if "yes" in response:
            return "yes"
        if "no" in response:
            return "no"
                
        # Default if response is invalid
        logging.warning(f"Invalid feature request response: '{response}'. Defaulting to 'no'")
        return "no"
    except Exception as e:
        logging.error(f"Feature request classification failed: {str(e)}")
        return "no"


def extract_competitor(review_text: str, model_name: str) -> str:
    """
    Extract which competitor brands are mentioned in the review.
    """
    if not review_text or not isinstance(review_text, str):
        return "none"
        
    prompt = f"""You are an expert at analyzing BMW app reviews. Identify any competitor car brands mentioned in this review:

"{review_text}"

CLASSIFICATION TASK:
Determine if the user mentions any BMW competitors and extract the specific competitor brand name(s).

DETAILED GUIDELINES:
- Extract ONLY car manufacturer brands EXPLICITLY mentioned in the review
- DO NOT infer or guess competitors that aren't directly mentioned
- If NO competitor is mentioned, return "none"
- [additional guidelines remain the same]

CRITICAL INSTRUCTION:
Only return a competitor name if it EXPLICITLY appears in the review text. Do not hallucinate brands.
"""

    try:
        response = run_ollama(prompt, model_name).strip().lower()
        
        # Clean response - remove any punctuation except commas
        response = response.replace('"', '').replace("'", '').replace(".", "").replace("!", "").replace("?", "")
        
        if "none" in response or not response:
            return "none"
        
        # VERIFICATION: Check if the response actually appears in the original text
        review_lower = review_text.lower()
        
        # Check each competitor name in the response
        competitors = response.split(',')
        verified_competitors = []
        
        for competitor in competitors:
            # Common name variations
            variations = {
                "mercedes": ["mercedes", "merc", "mercedes-benz", "mercedes benz"],
                "volkswagen": ["volkswagen", "vw", "volkswagon"],
                "chevrolet": ["chevrolet", "chevy"]
            }
            
            # Check if this competitor or its variations appear in the text
            if competitor in review_lower:
                verified_competitors.append(competitor)
                continue
                
            # Check variations if available
            if competitor in variations:
                for variation in variations[competitor]:
                    if variation in review_lower:
                        verified_competitors.append(competitor)
                        break
        
        if verified_competitors:
            return ",".join(verified_competitors)
        else:
            return "none"
            
    except Exception as e:
        logging.error(f"Competitor extraction failed: {str(e)}")
        return "none"


def analyze_review_step_by_step(review_text: str, model_name: str) -> Dict:
    """
    Analyze a review by performing each classification task separately.
    
    Args:
        review_text: The text of the review
        model_name: Name of the Ollama model to use
        
    Returns:
        Dict: Dictionary with all classification results
    """
    # Ensure the review text is a string
    if not isinstance(review_text, str):
        review_text = str(review_text) if review_text is not None else ""
    
    # Process each classification in sequence
    sentiment = classify_sentiment(review_text, model_name)
    topics = classify_topics(review_text, model_name)
    vehicle_type = classify_vehicle_type(review_text, model_name)
    user_experience = classify_user_experience(review_text, model_name)
    usage_profile = classify_usage_profile(review_text, model_name)
    is_pain_point = classify_pain_point(review_text, model_name)
    is_feature_request = classify_feature_request(review_text, model_name)
    competitor_mentioned = extract_competitor(review_text, model_name)
    
    # Return all results in a dictionary
    return {
        "sentiment": sentiment,
        "topics": topics,
        "vehicle_type": vehicle_type,
        "user_experience": user_experience,
        "usage_profile": usage_profile,
        "is_pain_point": is_pain_point,
        "is_feature_request": is_feature_request,
        "competitor_mentioned": competitor_mentioned
    }


def process_reviews_step_by_step(df: pd.DataFrame, model_name: str, batch_size: int = 10, 
                                start_batch: int = 1) -> pd.DataFrame:
    """
    Process all reviews with step-by-step individual classifications.
    
    Args:
        df: DataFrame with reviews in 'content_english' column
        model_name: Name of the Ollama model to use
        batch_size: Number of reviews to process per batch
        start_batch: Which batch to start processing from (for resuming)
        
    Returns:
        DataFrame with all classification results added
    """
    if 'content_english' not in df.columns:
        raise ValueError("Input DataFrame must contain 'content_english' column")
    
    # Create a copy of the DataFrame to avoid modifying the original
    result_df = df.copy()
    total_reviews = len(result_df)
    total_batches = (total_reviews + batch_size - 1) // batch_size
    
    # Initialize columns with default values (only if starting from the beginning)
    if start_batch == 1:
        result_df['sentiment'] = 'neutral'
        result_df['topics'] = 'other'
        result_df['vehicle_type'] = 'unclear'
        result_df['user_experience'] = 'unclear' 
        result_df['usage_profile'] = 'unclear'
        result_df['is_pain_point'] = 'no'
        result_df['is_feature_request'] = 'no'
        result_df['competitor_mentioned'] = 'none'
    
    logging.info(f"Starting step-by-step analysis from batch {start_batch}/{total_batches}")
    
    # Keep track of checkpoint filenames
    checkpoint_files = []
    
    # Process in batches
    for batch_num in range(start_batch, total_batches + 1):
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_reviews)
        batch_indices = result_df.index[start_idx:end_idx]
        
        logging.info(f"Processing batch {batch_num}/{total_batches} (reviews {start_idx+1}-{end_idx})")
        
        # Process each review in the batch
        for idx in tqdm(batch_indices, desc=f"Batch {batch_num}", unit="review"):
            review_text = result_df.loc[idx, 'content_english']
            
            # Skip empty reviews
            if pd.isna(review_text) or not str(review_text).strip():
                logging.warning(f"Skipping empty review at index {idx}")
                continue
            
            # Run all classifications
            try:
                results = analyze_review_step_by_step(str(review_text), model_name)
                
                # Update the DataFrame with results
                result_df.loc[idx, 'sentiment'] = results.get('sentiment', 'neutral')
                result_df.loc[idx, 'topics'] = results.get('topics', 'other')
                result_df.loc[idx, 'vehicle_type'] = results.get('vehicle_type', 'unclear')
                result_df.loc[idx, 'user_experience'] = results.get('user_experience', 'unclear')
                result_df.loc[idx, 'usage_profile'] = results.get('usage_profile', 'unclear')
                result_df.loc[idx, 'is_pain_point'] = results.get('is_pain_point', 'no')
                result_df.loc[idx, 'is_feature_request'] = results.get('is_feature_request', 'no')
                result_df.loc[idx, 'competitor_mentioned'] = results.get('competitor_mentioned', 'none')
                
            except Exception as e:
                logging.error(f"Error processing review at index {idx}: {e}")
                # Keep default values for this review
        
        # Save checkpoint after each batch
        checkpoint_filename = os.path.join(CHECKPOINT_DIR, f"batch_{batch_num}_of_{total_batches}.csv")
        batch_df = result_df.iloc[start_idx:end_idx].copy()
        batch_df.to_csv(checkpoint_filename, index=False)
        checkpoint_files.append(checkpoint_filename)
        logging.info(f"Saved checkpoint to {checkpoint_filename}")
        
        # Save progress information
        progress = {
            "last_completed_batch": batch_num,
            "total_batches": total_batches,
            "batch_size": batch_size,
            "total_reviews": total_reviews,
            "model_name": model_name,
            "last_processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=4)
        
        # Ask user if they want to continue
        if batch_num < total_batches:
            continue_processing = input(f"\nBatch {batch_num}/{total_batches} completed. Continue to next batch? (y/n): ")
            if continue_processing.lower() != 'y':
                logging.info(f"Processing paused after batch {batch_num}. Run again to continue from batch {batch_num + 1}.")
                return result_df  # Return the partially processed DataFrame
    
    # All batches completed, merge results
    logging.info("All batches completed. Merging results...")
    merge_checkpoints()
    
    return result_df

def merge_checkpoints():
    """Merge all checkpoint files into one consolidated file"""
    checkpoint_files = sorted(glob.glob(os.path.join(CHECKPOINT_DIR, "batch_*.csv")))
    
    if not checkpoint_files:
        logging.warning("No checkpoint files found to merge")
        return
    
    # Read and combine all checkpoint files
    dfs = []
    for file in checkpoint_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            logging.info(f"Added {file} to merge list ({len(df)} rows)")
        except Exception as e:
            logging.error(f"Error reading {file}: {e}")
    
    if not dfs:
        logging.error("No valid checkpoint files could be read")
        return
    
    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Save consolidated file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_filename = os.path.join(RESULTS_DIR, f"bmw_reviews_consolidated_{timestamp}.csv")
    
    # Save full results
    merged_df.to_csv(consolidated_filename, index=False)
    logging.info(f"Saved consolidated results with {len(merged_df)} reviews to {consolidated_filename}")
    
    # Print quick summary
    print(f"\n=== Classification Summary ({len(merged_df)} reviews) ===")
    for col in ['sentiment', 'vehicle_type', 'user_experience', 'usage_profile', 
               'is_pain_point', 'is_feature_request', 'competitor_mentioned']:
        print(f"\n{col.replace('_', ' ').title()} distribution:")
        print(merged_df[col].value_counts())

def run_analysis(df, model_name, batch_size=50):
    """Main function to run or resume analysis"""
    start_batch = 1
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    # Check if we have a progress file to resume from
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            
            last_batch = progress.get("last_completed_batch", 0)
            saved_total_batches = progress.get("total_batches", 0)
            prev_model = progress.get("model_name", "")
            last_time = progress.get("last_processed_time", "unknown time")
            
            if last_batch < total_batches:
                print(f"Previous run found (completed {last_batch}/{saved_total_batches} batches at {last_time}).")
                
                # Let user choose which batch to start from
                print(f"\nBatch information:")
                print(f"- Total batches: {total_batches}")
                print(f"- Completed batches: 1 to {last_batch}")
                print(f"- Remaining batches: {last_batch + 1} to {total_batches}")
                
                while True:
                    batch_input = input(f"\nEnter the batch number to start from (1-{total_batches}) or 'q' to quit: ")
                    
                    if batch_input.lower() == 'q':
                        logging.info("Analysis cancelled by user")
                        return None
                    
                    try:
                        selected_batch = int(batch_input)
                        if 1 <= selected_batch <= total_batches:
                            start_batch = selected_batch
                            logging.info(f"Starting from user-selected batch {start_batch}")
                            
                            # Warn if starting from an incomplete batch
                            if selected_batch <= last_batch:
                                overwrite = input(f"Batch {selected_batch} was already completed. Reprocess this batch? (y/n): ")
                                if overwrite.lower() != 'y':
                                    # User changed their mind - ask again
                                    continue
                            
                            # Warn if model changed
                            if prev_model and prev_model != model_name:
                                logging.warning(f"Using a different model ({model_name}) than previous run ({prev_model})")
                            
                            break
                        else:
                            print(f"Invalid batch number. Please enter a number between 1 and {total_batches}.")
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                print("Previous run completed all batches. Starting over.")
        except Exception as e:
            logging.error(f"Error reading progress file: {e}")
            print(f"Error reading progress file: {e}")
    else:
        print("No previous run found. Starting from the beginning.")
    
    # Start or resume processing
    print(f"Starting classification from batch {start_batch}...")
    start_time = time.time()
    
    df_classified = process_reviews_step_by_step(
        df=df,
        model_name=model_name,
        batch_size=batch_size,
        start_batch=start_batch
    )
    
    # Calculate elapsed time
    total_time = time.time() - start_time
    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Classification complete! Time taken: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    return df_classified

df_translated = pd.read_csv("bmw_app_analysis/translations/final_translated.csv")

# Run the full analysis (with resume capability)
df_classified = run_analysis(
    df=df_translated,
    model_name=ollama_model_name,
    batch_size=1000 # Process in batches of 5
)

# Final output is already saved as part of run_analysis
print("Classification complete!")
