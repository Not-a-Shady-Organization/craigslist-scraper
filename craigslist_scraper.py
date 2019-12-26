from Scraper import Scraper
import argparse
from utils import BadOptionsError, convert_to_date, makedir
import os
import logging
import json


LOG_DIR = os.environ.get('LOG_DIR', 'scraper-logs')
BUCKET = 'craig-the-poet'


def craigslist_scraper(destination_bucket_dir, url=None, city=None, count=None, min_word_count=None, max_word_count=None, date=None):
    ####################
    # VALIDATE OPTIONS #
    ####################

    if not destination_bucket_dir:
        raise BadOptionsError('Must specify location for ads to be stored')

    if not url and not city:
        raise BadOptionsError('Must specify either URL or CITY from which to scrape')

    ##########
    # SCRAPE #
    ##########

    # TODO: This probably shouldn't be a class to be real
    s = Scraper()

    # If we have a city to scrape
    if city:
        # TODO : This is so brittle. Make URL creation better... dict? allow bestof?
        ad_list_url = f'https://{city}.craigslist.org/d/missed-connections/search/mis'
        return s.scrape_ads_to_bucket(
            destination_bucket_dir,
            ad_list_url,
            count=count,
            min_word_count=min_word_count,
            max_word_count=max_word_count,
            date=date
        )

    # If given a URL
    if url:
        return s.scrape_ad_to_bucket(
            destination_bucket_dir,
            url
        )


def next_log_file(log_directory):
    files = os.listdir(log_directory)
    if files:
        greatest_num = max([int(filename.replace('log-', '').replace('.txt', '')) for filename in files])
        return f'log-{greatest_num+1}.txt'
    return 'log-0.txt'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination-bucket-dir', help='Destination bucket subdirectory within "craigslist-ads/"')

    # Sources
    parser.add_argument('--url', help='URL of craigslist missed connections ads to scrape')

    parser.add_argument('--city', help='City from which to scrape craigslist missed connections ads')
    parser.add_argument('--count', type=int, default=10, help='With CITY, How many ads to scrape')

    # Filters
    parser.add_argument('--date', type=convert_to_date, help='Only scrape ads posted on this date')
    parser.add_argument('--min-word-count', type=int, help='Only scrape ads whose bodies contain more than this number of words')
    parser.add_argument('--max-word-count', type=int, help='Only scrape ads whose bodies contain less than this number of words')

    args = parser.parse_args()

    # Setup for logging
    makedir(LOG_DIR)
    log_filename = next_log_file(LOG_DIR)
    LOG_FILEPATH = f'{LOG_DIR}/{log_filename}'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
    logging.basicConfig(filename=LOG_FILEPATH, level=LOG_LEVEL)
    from LogDecorator import LogDecorator

    ret = craigslist_scraper(**vars(args))
    logging.info(f'Program returned {ret}')
    print(ret)
