#!/bin/bash
# Setup script for Streamlit deployment

# Download NLTK data
python -m nltk.downloader punkt stopwords wordnet

# Verify spaCy model is installed
python -c "import spacy; spacy.load('en_core_web_sm')" || python -m spacy download en_core_web_sm

echo "Setup complete!"