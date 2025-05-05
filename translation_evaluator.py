#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Evaluate translations of app reviews by scoring on a scale of 1-5.
"""

import pandas as pd
import requests
import time
from tqdm import tqdm
import os
import re

def evaluate_translations(input_file, output_file, model='llama3.1:8b', max_retries=2, timeout=60):
    print(f"Starting evaluation with {model}...")
    
    # Quick API test
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print(f"⚠️ Ollama API error: {response.status_code}")
            return
    except Exception as e:
        print(f"⚠️ Ollama not running: {e}")
        return
    
    # Load CSV
    try:
        df = pd.read_csv(input_file, sep=';')
        print(f"Loaded {len(df)} records")
    except Exception:
        try:
            df = pd.read_csv(input_file, sep=None, engine='python')
            print(f"Loaded {len(df)} records with auto-detection")
        except Exception as e:
            print(f"⚠️ Failed to load CSV: {e}")
            return
    
    # Initialize columns
    df['Score_A'] = None
    df['Score_B'] = None
    df['Winner'] = None
    
    def get_score(text):
        """Extract numeric score from response, ignoring thinking sections"""
        # Remove thinking sections
        while "<think>" in text and "</think>" in text:
            think_start = text.find("<think>")
            think_end = text.find("</think>", think_start) + len("</think>")
            if think_start >= 0 and think_end > 0:
                text = text[:think_start] + text[think_end:]
            else:
                break
        
        # Alternative regex approach if the above doesn't work
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        # Clean up the remaining text
        text = text.strip()
        
        # Look for the score (prioritize the last digit as the final answer)
        if text:
            # First check if the response ends with a digit
            if text[-1] in "12345":
                return int(text[-1])
            
            # Then check from the end backward
            for i in range(len(text)-1, -1, -1):
                if text[i] in "12345":
                    return int(text[i])
            
            # Finally, check the whole text
            for char in text:
                if char in "12345":
                    return int(char)
        
        return None
    
    def evaluate_single(original, translation, language, label):
        prompt = f"""Evaluate this translation of a MyBMW app review from {language} to English:

Original ({language}): {original}
Translation: {translation}

These are user reviews about the MyBMW mobile application, which may contain automotive terminology, app features, and user experience feedback.

Rate on a scale of 1-5 based on these criteria:
1: VERY POOR - Completely incorrect or incomprehensible translation
2: POOR - Major meaning errors or serious mistranslations
3: FAIR - Conveys basic meaning but has notable accuracy or fluency issues
4: GOOD - Mostly accurate with only minor issues in wording or naturalness
5: EXCELLENT - Perfect translation that captures meaning, tone, and reads naturally

IMPORTANT: Use the FULL RANGE of scores (1-5). Don't hesitate to give 1s for poor translations or 5s for excellent ones.

Focus on: accuracy, preservation of tone, natural English expression, and completeness.

Your response must be ONLY a single digit: 1, 2, 3, 4, or 5."""

        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    response_text = response.json().get('response', '').strip()
                    score = get_score(response_text)
                    
                    if score:
                        return score
                    else:
                        print(f"⚠️ Couldn't extract score from: '{response_text[:30]}...'")
                
                if attempt < max_retries:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error: {e}")
                if attempt < max_retries:
                    time.sleep(2)
                else:
                    return "ERROR"
                    
        return "ERROR"
    
    # Process reviews
    errors = 0
    print("\nEvaluating translations:")
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Progress"):
        lang = row['language']
        
        # Get scores
        score_a = evaluate_single(row['content'], row['Translation A'], lang, "A")
        score_b = evaluate_single(row['content'], row['Translation B'], lang, "B")
        
        # Determine winner
        if isinstance(score_a, int) and isinstance(score_b, int):
            if score_a > score_b:
                winner = "A"
            elif score_b > score_a:
                winner = "B"
            else:
                winner = "Tie"
        else:
            winner = "Error"
            errors += 1
            
        # Store results
        df.at[idx, 'Score_A'] = score_a
        df.at[idx, 'Score_B'] = score_b
        df.at[idx, 'Winner'] = winner
        
        # Show just last row result in one line
        tqdm.write(f"Row {idx+1}: {lang} - A({score_a}) vs B({score_b}) → {winner}")
        
        # Save progress
        df.to_csv(output_file, index=False, sep=';')
    
    # Summary statistics
    print("\n=== RESULTS ===")
    
    valid_df = df[df['Winner'] != 'Error'].copy()
    if len(valid_df) > 0:
        # Convert scores to numeric for calculations
        valid_df['Score_A'] = pd.to_numeric(valid_df['Score_A'], errors='coerce')
        valid_df['Score_B'] = pd.to_numeric(valid_df['Score_B'], errors='coerce')
        
        # Overall statistics
        a_wins = (valid_df['Winner'] == 'A').sum()
        b_wins = (valid_df['Winner'] == 'B').sum()
        ties = (valid_df['Winner'] == 'Tie').sum()
        avg_score_a = valid_df['Score_A'].mean()
        avg_score_b = valid_df['Score_B'].mean()
        
        print(f"Overall (n={len(valid_df)}):")
        print(f"- Win rate: A: {a_wins} ({a_wins/len(valid_df)*100:.1f}%), " +
              f"B: {b_wins} ({b_wins/len(valid_df)*100:.1f}%), " +
              f"Ties: {ties} ({ties/len(valid_df)*100:.1f}%)")
        print(f"- Average scores: A: {avg_score_a:.2f}, B: {avg_score_b:.2f}, Difference: {avg_score_a-avg_score_b:.2f}")
        
        # Results by language
        print("\nBy language:")
        for lang in df['language'].unique():
            lang_df = valid_df[valid_df['language'] == lang]
            if len(lang_df) > 0:
                a_lang = (lang_df['Winner'] == 'A').sum()
                b_lang = (lang_df['Winner'] == 'B').sum()
                t_lang = (lang_df['Winner'] == 'Tie').sum()
                
                lang_avg_a = lang_df['Score_A'].mean()
                lang_avg_b = lang_df['Score_B'].mean()
                
                print(f"{lang} (n={len(lang_df)}):")
                print(f"- Win rate: A: {a_lang} ({a_lang/len(lang_df)*100:.1f}%), " +
                      f"B: {b_lang} ({b_lang/len(lang_df)*100:.1f}%), " +
                      f"Ties: {t_lang} ({t_lang/len(lang_df)*100:.1f}%)")
                print(f"- Average scores: A: {lang_avg_a:.2f}, B: {lang_avg_b:.2f}, Diff: {lang_avg_a-lang_avg_b:.2f}")
    
    print(f"\nComplete! Results saved to {output_file}")
    return df

if __name__ == "__main__":
    evaluate_translations(
        input_file="bmw_app_analysis/translations/bmw_reviews_sampledHE.csv",
        output_file="bmw_app_analysis/translations/bmw_reviews_evaluated_1to5.csv",
        model="qwen3:14b"
    ) 