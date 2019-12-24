import requests
from bs4 import BeautifulSoup
from LogDecorator import LogDecorator
from google_utils import upload_string_to_bucket, download_as_string
import sys
from datetime import datetime
import hashlib
from utils import clean_word, convert_to_date, date_matches_craigslist_date


class AdTooShortException(Exception):
    pass

class AdAlreadyInBucketException(Exception):
    pass


class Scraper():
    def __init__(self, **kwargs):
        pass

    def get_ledger(self, ledger_filepath):
        # Either download the ledger, or create one, then download it
        try:
            ledger = download_as_string('craig-the-poet', ledger_filepath)
        except:
            upload_string_to_bucket('craig-the-poet', '', ledger_filepath)
            ledger = download_as_string('craig-the-poet', ledger_filepath)
        return ledger


    @LogDecorator()
    def scrape_ad_to_bucket(self, ad_url, destination_bucket_dir=None, min_word_count=None, date=None):
        if min_word_count:
            min_word_count = int(min_word_count)

        # Get the ad
        try:
            obj = self.scrape_craigslist_ad(ad_url)
        except AttributeError as e:
            raise e

        # If the ads is from the wrong date
        if date and not date_matches_craigslist_date(date, obj['ad-posted-time']):
            return False

        title = obj['title']
        body = obj['body']
        ad_posted_time = obj['ad-posted-time']
        city = self.get_city_from_url(ad_url)
        hash = hashlib.sha256(obj['body'].encode()).hexdigest()
        dir = city if not destination_bucket_dir else destination_bucket_dir
        time = str(datetime.now())

        if min_word_count and len(body.split(' ')) < min_word_count:
            raise AdTooShortException('Requested ad was below the minimum word count')

        # Pull the ledger to later check if we've DL'd the ad already
        bucket_ledger = f'craigslist/{dir}/ledger.txt'
        ledger = self.get_ledger(bucket_ledger)
        hashes = ledger.split('\n')

        # If we've seen the hash, skip this ad
        if hash in hashes:
            raise AdAlreadyInBucketException()


        # Add hash to seen hashes and upload this ad
        metadata = {
            # Currently unused, but could confirm ledger accuracy
            'hash': hash,

            # These metadata are passed onto the video poem when generated
            'ad-url': ad_url,
            'ad-title': title, # As we need to clean the title in most circumstances, this metadata will preserve the original title
            'ad-posted-time': ad_posted_time,
            'ad-body-word-count': len(body.split()),

            'in-use': False, # Signifies an ad is already being made into a poem
            'failed': False, # Signifies an ad has failed the poem making process (and shouldn't be used)
            'used': False # Signifies an ad has already been made into a poem
        }

        text = title + '\n' + body
        destination_filepath = f'craigslist/{dir}/{clean_word(title)}.txt'
        upload_string_to_bucket('craig-the-poet', text, destination_filepath, metadata)

        hashes.append(hash)
        new_ledger = '\n'.join(hashes)
        upload_string_to_bucket('craig-the-poet', new_ledger, bucket_ledger)

        return True



    @LogDecorator()
    def scrape_ads_to_bucket(self, ad_list, count, destination_bucket_dir=None, min_word_count=None, date=None):
        count = int(count)
        if min_word_count:
            min_word_count = int(min_word_count)

        # TODO : Add abstraction via generator function to allow counts > one page of ads
        result_page = requests.get(ad_list)
        result_soup = BeautifulSoup(result_page.text, 'html.parser')

        # Scrape all ad URLs from ad list page
        urls = []
        for ad_title in result_soup.find_all('a', {'class':'result-title'}):
            urls.append(ad_title['href'])

        successful_uploads = 0
        for i, url in enumerate(urls):
            try:
                if self.scrape_ad_to_bucket(url, destination_bucket_dir=destination_bucket_dir, min_word_count=min_word_count, date=date):
                    successful_uploads += 1

                if successful_uploads >= count:
                    return successful_uploads
            except AdTooShortException:
                pass
            except AdAlreadyInBucketException:
                pass
            except AttributeError:
                pass
        return successful_uploads


    # TODO: Only works for CL
    @LogDecorator()
    def get_city_from_url(self, url):
        return url.replace('http://', '').replace('https://', '').split('.')[0]



    # TODO: Make more sophisticated. Handle cases where e.g. CL ad is titles YELP BOY TASTY
    @LogDecorator()
    def classify(self, url):
        if 'craigslist' in url:
            return 'craigslist'

        if 'yelp' in url:
            return 'yelp'


    # TODO: Add more scrapers for more sites
    @LogDecorator()
    def scrape_craigslist_ad(self, ad_url):
        result_page = requests.get(ad_url)
        result_soup = BeautifulSoup(result_page.text, 'html.parser')

        # Get Craigslist title
        result_title_element = result_soup.find(id='titletextonly')
        result_title = result_title_element.text

        result_time_element = result_soup.find('time')
        ad_posted_time = result_time_element['datetime']

        # Get Craigslist body
        result_body_element = result_soup.find(id='postingbody')
        bad_text = 'QR Code Link to This Post'
        result_text = [x for x in result_body_element.text.split('\n') if x != bad_text and x != '']
        result_body = '\n'.join(result_text)

        return {'title': result_title, 'body': result_body, 'ad-posted-time': ad_posted_time}
