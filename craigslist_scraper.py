from Scraper import Scraper
import argparse
from utils import BadOptionsError, convert_to_date, makedir
import os
import logging


def craigslist_scraper(url=None, destination_bucket_dir=None, city=None, count=None, min_word_count=None, date=None):
    ####################
    # VALIDATE OPTIONS #
    ####################

    if not url and not city:
        raise BadOptionsError('Must specify either URL or CITY from which to scrape')

    if url:
        logging.warning('As a particular ad\'s URL is specified, all options COUNT, MIN_WORD_COUNT, CITY, and DATE are disregarded')

    if city and not count:
        logging.warning('As COUNT is not specified, default of 100 ads will be used')


    s = Scraper()

    # If we have a specific ad to scrape
    if url:
        s.scrape_ad_to_bucket(url, destination_bucket_dir=destination_bucket_dir)
        return 1

    # If we have a city to scrape
    if city:
        # TODO : This is so brittle
        ad_list_url = f'https://{city}.craigslist.org/d/missed-connections/search/mis'
        count_scraped = s.scrape_ads_to_bucket(ad_list_url, count, destination_bucket_dir=destination_bucket_dir, min_word_count=min_word_count, date=date)
        return count_scraped


def next_log_file(log_directory):
    files = os.listdir(log_directory)
    if files:
        greatest_num = max([int(filename.replace('log-', '').replace('.txt', '')) for filename in files])
        return f'log-{greatest_num+1}.txt'
    return 'log-0.txt'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL of single craigslist missed connections ad to scrape')
    parser.add_argument('--city', help='City from which to scrape craigslist missed connections ads')
    parser.add_argument('--count', type=int, default=100, help='With city, how many ads to scrape')
    parser.add_argument('--date', type=convert_to_date, help='Only scrape ads posted on this date')
    parser.add_argument('--min-word-count', type=int, help='URL of single craigslist missed connections ad to scrape')
    parser.add_argument('--destination-bucket-dir', help='Destination bucket, if not the ad\'s city')

    args = parser.parse_args()

    # Setup for logging
    LOG_DIR = 'scraper-logs'
    makedir(LOG_DIR)
    log_filename = next_log_file(LOG_DIR)
    LOG_FILEPATH = f'{LOG_DIR}/{log_filename}'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
    logging.basicConfig(filename=LOG_FILEPATH, level=LOG_LEVEL)
    from LogDecorator import LogDecorator

    count_scraped = craigslist_scraper(**vars(args))
    logging.info(f'We scraped {count_scraped} ad(s)')
