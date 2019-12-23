from flask import Flask, request
from craigslist_scraper import craigslist_scraper
import os

app = Flask(__name__)

@app.route('/',  methods=['GET'])
def hello_world():
    return 'We are live :)'

@app.route('/', methods=['POST'])
def kickoff_scraper():
    data = request.get_json()
    craigslist_scraper(**data)
    return f'Job received: {str(data)}'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
