from flask import Flask, request
from craigslist_scraper import craigslist_scraper
import os

app = Flask(__name__)

@app.route('/',  methods=['GET'])
def hello_world():
    return 'Craigslist Scraper is live :)'

@app.route('/', methods=['POST'])
def kickoff_scraper():
    data = request.get_json()
    try:
        return str(craigslist_scraper(**data))
    except Exception as e:
        return f'Exception occurred: {e}'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
