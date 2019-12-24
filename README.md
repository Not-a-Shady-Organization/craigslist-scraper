# Craigslist Scraper

## Local
#### Setup
The scraper uses `not-shady-utils`, thus we need a local copy of the utils repo. We point to that instance in our `PYTHONPATH` as...

```bash
git clone https://github.com/Not-a-Shady-Organization/not-shady-utils.git
export PYTHONPATH=$PYTHONPATH:path/to/not-shady-utils
```

To allow access to our GCP resources we use...

```bash
export GOOGLE_APPLICATION_CREDENTIALS=path/to/auth-key-file.json
```

And finally, to install dependencies...

```bash
pip install -r requirements.txt
```

#### Run
The scraper may scrape `COUNT` many ads from missed connections for `CITY` as...

```bash
python craigslist_scraper.py --city [CITY] --count [COUNT]
```

with optional `--min-word-count` argument to filter for longer ads. Also optional, `--date` lets us filter to ads from a specific day (format mm-dd-yyyy). We also can scrape a particular ad at `URL`, placing the ad into `BUCKET_DIR` as...

```bash
python craigslist_scraper.py --url [URL] --bucket-dir [BUCKET_DIR]
```

##### Examples
```bash
python craigslist_scraper.py --city london --count 60
```

```bash
python craigslist_scraper.py --city portland --count 10 --min-word-count 50
```

```bash
python craigslist_scraper.py --url https://portland.craigslist.org/mlt/mis/d/portland-heather-red-haired-beauty/7042927716.html --bucket-dir awesome-ads
```

## Dockerized
*There's probably a way around these steps, but for now this will work.*

#### Setup
- Copy auth-file-key.json for the GCP project to this directory
- Clone the utils repo into this repo at `./not-shady-utils`

```bash
git clone https://github.com/Not-a-Shady-Organization/not-shady-utils.git
```

Probably better to create a utils volume and mount it to all containers that need it.

#### Build
To build the container image locally, use...

```bash
docker image build -t cl-scraper:1.0 .
```

TODO: We should create a dockerhub instance for these and pull from that

#### Run
By spinning up the built container and sending a POST request with a JSON body request, we can interact with the HTTP container. *Note* -- these commands will get responses before the process is complete.

##### Examples
```bash
{
  "city": "duluth",
  "count": 10,
  "date": "12-25-2019"
}
```

#### Push to Cloud Run
To push our image to GCP's Cloud Run for event based runs, we build as above, then...

```bash
docker tag cl-scraper:[TAG] us.gcr.io/ccblender/craigslist-scraper:[TAG]
docker push us.gcr.io/ccblender/craigslist-scraper:[TAG]
```

Then, hop onto Cloud Run on the GCP Console. Select the `craigslist-scraper` service and select `Deploy New Revision`. We should see our newly uploaded container in the list. Revise and wait for it to go live. Hitting the given endpoint with a browser will return a "We are live :)" message when the container is ready for requests.


## Notes On Cloud Scheduler Jobs
Cloud Scheduler does not let you set the `Content-Type` header from the web interface [[1]](https://stackoverflow.com/questions/53216177/http-triggering-cloud-function-with-cloud-scheduler). They do however let you set the headers from the cli. So, to create new jobs we must write commands like this...

```bash
gcloud scheduler jobs create http portland-scraper-job \
  --schedule "0 12 * * *" \
  --time-zone "PST" \
  --uri "https://craigslist-scraper-ekdapyzpva-uc.a.run.app" \
  --http-method POST \
  --headers Content-Type=application/json \
  --message-body="{
    \"city\": \"portland\",
    \"count\": \"50\",
    \"min_word_count\": \"30\"
  }"\
  --description="Scrape Portland for 50 ads over 30 words"
```

For details, checkout the relevant [GCloud CLI reference](https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/create/pubsub) and this [cron job doc](https://cloud.google.com/scheduler/docs/creating#) and also this [cron syntax helper](https://crontab.guru/every-day-8am). :)
