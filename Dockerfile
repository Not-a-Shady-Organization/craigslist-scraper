# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# Get source files & API key
COPY craigslist_scraper.py requirements.txt auth-key-file.json app.py Scraper.py ./

COPY not-shady-utils /usr/local/not-shady-utils

# Note credential location for use of Google/YouTube APIs
ENV GOOGLE_APPLICATION_CREDENTIALS=./auth-key-file.json

# Note where to find utils functions
ENV PYTHONPATH=$PYTHONPATH:usr/local/not-shady-utils

# Install dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
