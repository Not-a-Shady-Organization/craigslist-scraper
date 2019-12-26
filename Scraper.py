import requests
from bs4 import BeautifulSoup
from LogDecorator import LogDecorator
from google_utils import upload_string_to_bucket, download_as_string
import sys
from datetime import datetime
import hashlib
from utils import clean_word, convert_to_date, craigslist_format_to_date




class Scraper():
    def __init__(self, **kwargs):
        pass


    @LogDecorator()
    def scrape_ad_to_bucket(self, destination_bucket_dir, ad_url, min_word_count=None, max_word_count=None):
        # Ensure things are typed correctly
        min_word_count = int(min_word_count) if min_word_count else None
        max_word_count = int(max_word_count) if max_word_count else None

        # Get the ad
        try:
            obj = self.scrape_craigslist_ad(ad_url)
        except AttributeError as e:
            raise e

        title = obj['title']
        body = obj['body']
        ad_posted_time = obj['ad-posted-time']
        city = self.get_city_from_url(ad_url)

        word_count = len(body.split(' '))

        if (min_word_count and word_count < min_word_count) or (max_word_count and word_count > max_word_count):
            raise Exception(f'Requested ad had {word_count} words. Out of word count range ({min_word_count}, {max_word_count})')

        metadata = {
            # These metadata are passed onto the video poem when generated
            'ad-url': ad_url,
            'ad-title': title, # As we need to clean the title in most circumstances, this metadata will preserve the original title
            'ad-posted-time': ad_posted_time,
            'ad-body-word-count': word_count,

            'in-use': False, # Signifies an ad is already being made into a poem
            'failed': False, # Signifies an ad has failed the poem making process (and shouldn't be used)
            'used': False # Signifies an ad has already been made into a poem
        }

        # Upload the ad with it's metadata
        text = title + '\n' + body
        bucket_filepath = f'craigslist/{destination_bucket_dir}/{clean_word(title)}.txt'
        upload_string_to_bucket('craig-the-poet', text, bucket_filepath, metadata)

        return bucket_filepath



    @LogDecorator()
    def scrape_ads_to_bucket(self, destination_bucket_dir, ad_list_url, count=None, min_word_count=None, max_word_count=None, date=None):
        # Ensure things are typed correctly
        count = int(count) if count else None
        min_word_count = int(min_word_count) if min_word_count else None
        max_word_count = int(max_word_count) if max_word_count else None
        if date:
            if type(date) == str:
                date = convert_to_date(date)

        # TODO : Add abstraction via generator function to allow counts > one page of ads

        # Grab the HTML source code
        result_page = requests.get(ad_list_url)
        result_soup = BeautifulSoup(result_page.text, 'html.parser')

        # Scrape all ad URLs from ad list page
        ad_urls = []
        for ad_element in result_soup.find_all('li', {'class':'result-row'}):

            # Check date to allow for filtering
            datetime_string = ad_element.find('time')['datetime']
            datetime_obj = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M")
            url = ad_element.find('a')['href']

            # If date is filtered, skip any non-matching dates
            if date and datetime_obj.date() != date.date():
                continue

            # Check if it's "nearby" meaning not in the location we want
            nearby_element = ad_element.find('span', {'class': 'nearby'})
            if nearby_element:
                continue

            # Note the URL
            ad_urls += [url]

        # Scrape the filtered URLs
        successful_uploads = 0
        bucket_paths = []
        for url in ad_urls:
            try:
                bucket_path = self.scrape_ad_to_bucket(
                    destination_bucket_dir=destination_bucket_dir,
                    ad_url=url,
                    min_word_count=min_word_count,
                    max_word_count=max_word_count
                )
                bucket_paths += [bucket_path]
                successful_uploads += 1

                if count and successful_uploads >= count:
                    break

            except Exception as e:
                print(e)

        return bucket_paths



    # TODO: Only works for CL
    @LogDecorator()
    def get_city_from_url(self, url):
        return url.replace('http://', '').replace('https://', '').split('.')[0]



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
