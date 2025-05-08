#!/bin/bash

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit is not installed. Installing requirements..."
    pip install -r requirements.txt
fi

# Run the dashboard
echo "Starting MyBMW App Review Analysis Dashboard..."
streamlit run dashboard.py 