from Scraper import Scraper
import argparse

'''
This script is meant to be called with either { city and count } or a { url and bucket_dir }.
City and count will pull count many ads from that city (note cities like New
York must be type newyork for now). You can also grab a single ad using URL and
post it to a specific bucket, specified by bucket_dir. Min word count is used to grab
only longer ads from a city.

e.g. python craigslist_scraper.py --city portland --count 60 --min-word-count 30
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', help='City from which to scrape craigslist missed connections ads')
    parser.add_argument('--count', type=int, help='With city, how many ads to scrape')

    parser.add_argument('--url', help='URL of single craigslist missed connections ad to scrape')
    parser.add_argument('--bucket-dir', help='Destination bucket, if not the ad\'s city')

    parser.add_argument('--min-word-count', type=int, help='URL of single craigslist missed connections ad to scrape')

    args = parser.parse_args()

    if not (args.url and args.bucket_dir) and not (args.city and args.count):
        print('Must specify --city and --count, or a specific ad --url and --bucket-dir. Exiting...')
        exit()

    # TODO : This is so brittle
    ad_list_url = f'https://{args.city}.craigslist.org/d/missed-connections/search/mis'

    s = Scraper()

    if args.url:
        s.scrape_ad_to_bucket(args.url, bucket_dir=args.bucket_dir)
    else:
        s.scrape_ads_to_bucket(ad_list_url, args.count, bucket_dir=args.bucket_dir, min_word_count=args.min_word_count)
