from Scraper import Scraper
import argparse
from utils import BadOptionsError, convert_to_date

'''
This script is meant to be called with either { city and count } or a { url and bucket_dir }.
City and count will pull count many ads from that city (note cities like New
York must be type newyork for now). You can also grab a single ad using URL and
post it to a specific bucket, specified by bucket_dir. Min word count is used to grab
only longer ads from a city.

e.g. python craigslist_scraper.py --city portland --count 60 --min-word-count 30
'''

# TODO Move scraper into file
# TODO Make returns meaningful

def craigslist_scraper(url=None, destination_bucket_dir=None, city=None, count=None, min_word_count=None, date=None):
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL of single craigslist missed connections ad to scrape')
    parser.add_argument('--city', help='City from which to scrape craigslist missed connections ads')
    parser.add_argument('--count', type=int, default=100, help='With city, how many ads to scrape')
    parser.add_argument('--date', type=convert_to_date, help='Only scrape ads posted on this date')
    parser.add_argument('--min-word-count', type=int, help='URL of single craigslist missed connections ad to scrape')
    parser.add_argument('--destination-bucket-dir', help='Destination bucket, if not the ad\'s city')

    args = parser.parse_args()

    ####################
    # VALIDATE OPTIONS #
    ####################

    if not args.url and not args.city:
        raise BadOptionsError('Must specify either --url or --city from which to scrape')

    if args.url:
        print('As a particular ad\'s URL is specified, all options --count, --min-word-count, --date, and --city are disregarded')

    if args.city and not args.count:
        print('As --count is not specified, default of 100 ads will be used')

    count_scraped = craigslist_scraper(**vars(args))
    print(f'We scraped {count_scraped} ad(s)')
