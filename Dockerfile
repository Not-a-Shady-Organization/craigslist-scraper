FROM python:3

# Get source files & API key
COPY craigslist_scraper.py requirements.txt auth-key-file.json ./

COPY not-shady-utils /usr/local/not-shady-utils

# Note credential location for use of Google/YouTube APIs
ENV GOOGLE_APPLICATION_CREDENTIALS=./auth-key-file.json

# Note where to find utils functions
ENV PYTHONPATH=$PYTHONPATH:usr/local/not-shady-utils

RUN pip3 install -r requirements.txt
