# BMW App Review Analysis

This repository contains code to analyze reviews for the BMW Connected App. The project fetches reviews from the Google Play Store, translates non-English reviews, and performs sentiment and topic analysis using an OLLAMA model. The processed results are then visualized via dashboards and comprehensive reports.

## Features

- **Review Fetching:** Retrieve app reviews across multiple languages from the Google Play Store.
- **Translation:** Automatically translate non-English reviews to English.
- **Sentiment Analysis:** Classify reviews as **Positive**, **Negative**, or **Neutral** using the OLLAMA model.
- **Topic Analysis:** Categorize reviews based on predefined topics (e.g., UI/UX, Performance, Connectivity, etc.).
- **Data Visualization:** Generate insightful visualizations and dashboards using libraries like Matplotlib and Streamlit.
- **Comprehensive Reporting:** Produce detailed analysis reports highlighting sentiment distribution, ratings, and review trends.

## Project Structure

- `data_processing.py`: Contains functions to fetch, sample, translate, and analyze reviews. Also computes additional metrics like sentiment and topic distributions.
- `dashboard.py`: Implements a Streamlit dashboard for interactive visualization of the processed review data.
- `MyBMWappSent.ipynb`: A Jupyter Notebook for exploring sentiment analysis and the review data.
- `bmw_app_comprehensive_analysis_report.txt`: A sample comprehensive report generated from the processed data.
- `YoutubeSourceBMW.ipynb`: A placeholder Notebook for potential integration with YouTube content related to the app.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/project-for-bmw.git
   cd project-for-bmw
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies:**

   If you have a `requirements.txt` file available:
   ```bash
   pip install -r requirements.txt
   ```
   Otherwise, install the following packages manually:
   - pandas
   - tqdm
   - matplotlib
   - google_play_scraper
   - networkx
   - streamlit
   - (and any additional dependencies required by your project)

## Usage

### Data Processing and Analysis

Run the main data processing pipeline to fetch, translate, and analyze the reviews:

```bash
python3 data_processing.py
```

This script will:
- Fetch and sample reviews from the Google Play Store.
- Translate non-English reviews.
- Run sentiment and topic analyses.
- Output processed data along with summary metrics in the console.

### Dashboard

Launch the Streamlit dashboard to interactively explore the review data:

```bash
streamlit run dashboard.py
```

A new browser window should open displaying:
- Sentiment distributions
- Ratings trends
- Topic analysis visualizations
- Additional interactive metrics

## Configuration

- **Google Play App ID:** Ensure that the `APP_ID` variable in `data_processing.py` is set to your target app (e.g., `"de.bmw.connected.mobile20.row"`).
- **Model Settings:** Verify the `OLLAMA_MODEL_NAME` and prompts (e.g., `OLLAMA_PROMPT_TEMPLATE`) in `data_processing.py` are correctly configured for your analysis needs.

## Contributing

Contributions, issues, and feature requests are welcome! Please feel free to open an issue or submit a pull request for any enhancements or fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.