"""
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
"""


import sys

import LNEx as lnex

import json
from tabulate import tabulate

def read_tweets():

    tweets_file = "_Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets


def run_test_using_files():

    with open("_Data/chennai_geo_locations.json") as f:
        geo_locations = json.load(f)

    # with open("_Data/chennai_geo_info.json") as f:
    #    json.load(f)

    with open("_Data/chennai_extended_english_words.json") as f:
        extended_words3 = json.load(f)

    lnex.initialize_using_files(geo_locations, extended_words3)

    header = [
    "tweet_mention",
    "mention_offsets",
    "geo_location",
    "geo_info_id"]

    for tweet in read_tweets():

        print tweet

        rows = list()
        for x in lnex.extract(tweet):
            row = x[0], x[1], x[2], x[3]
            rows.append(row)

        print "-" * 90
        print tabulate(rows, headers=header)
        print "-" * 90


def run_text_using_elasticindex():

    lnex.set_connection_string('130.108.85.186:9200')

    # chennai flood bounding box
    chennai_bb = [12.74, 80.066986084,
                  13.2823848224, 80.3464508057]

    lnex.initialize(chennai_bb)

    header = [
    "tweet_mention",
    "mention_offsets",
    "geo_location",
    "geo_info_id"]

    for tweet in read_tweets():

        print tweet

        rows = list()
        for x in lnex.extract(tweet):
            row = x[0], x[1], x[2], x[3]
            rows.append(row)

        print "-" * 90
        print tabulate(rows, headers=header)
        print "-" * 90


if __name__ == "__main__":

    #run_test_using_files()
    run_text_using_elasticindex()
