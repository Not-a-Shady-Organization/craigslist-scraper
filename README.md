# Craigslist Scraper

## Local
### Setup
The scraper uses `not-shady-utils`, thus we need a local copy of the utils repo. We point to that instance in our `PYTHONPATH` as...

`export PYTHONPATH=$PYTHONPATH:path/to/not-shady-utils`

To allow access to our GCP resources we use...

`export GOOGLE_APPLICATION_CREDENTIALS=path/to/auth-key-file.json`

And finally, to install dependencies...

`pip install -r requirements.txt`

### Run
The scraper may scrape `COUNT` many ads from missed connections for `CITY` as...

`python craigslist_scraper.py --city [CITY] --count [COUNT]`

with optional `--min-word-count` option to filter for longer ads. We also can scrape a particular ad at `URL`, placing the ad into `BUCKET_DIR` as...

`python craigslist_scraper.py --url [URL] --bucket-dir [BUCKET_DIR]`

#### Examples
`python craigslist_scraper.py --city london --count 60`

`python craigslist_scraper.py --city portland --count 10 --min-word-count 50`

`python craigslist_scraper.py --url https://portland.craigslist.org/mlt/mis/d/portland-heather-red-haired-beauty/7042927716.html --bucket-dir awesome-ads`


## Dockerized
*There's probably a way around these steps, but for now this will work.*

### Setup
- Copy auth-file-key.json for the GCP project to this directory
- Clone the utils repo into this repo at `./not-shady-utils`

`git clone https://github.com/Not-a-Shady-Organization/not-shady-utils.git`

Probably better to create a utils volume and mount it to all containers that need it.

### Build
To build the container image locally, use...

`docker image build -t cl-scraper:1.0 .`

TODO: We should create a dockerhub instance for these and pull from that

### Run
By calling the built container and passing it a command, we can use the scraping script. *Note* -- these commands will return before the process is complete. Use `docker ps` to see if the container is still running.

#### Examples
`docker run -dt cl-scraper:1.0 python craigslist_scraper.py --city portland --count 2 --min-word-count 30`
