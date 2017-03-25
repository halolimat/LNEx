"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import sys
import json
import unicodedata
from tabulate import tabulate

import LNEx as lnex

################################################################################
################################################################################

def strip_non_ascii(s):
    if type(s) == unicode:
        nfkd = unicodedata.normalize('NFKD', s)
        return str(nfkd.encode('ASCII', 'ignore').decode('ASCII'))
    else:
        return s

################################################################################

def read_tweets():

    tweets_file = "_Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets

################################################################################

def init_using_files():

    with open("_Data/chennai_geo_locations.json") as f:
        geo_locations = json.load(f)

    with open("_Data/chennai_geo_info.json") as f:
        geo_info = json.load(f)

    with open("_Data/chennai_extended_words3.json") as f:
        extended_words3 = json.load(f)

    lnex.initialize_using_files(geo_locations, extended_words3)

    return geo_info

################################################################################

def init_using_elasticindex():

    lnex.elasticindex(conn_string='130.108.85.186:9200', index_name="photon_v1")

    # chennai flood bounding box
    chennai_bb = [12.74, 80.066986084, 13.2823848224, 80.3464508057]

    return lnex.initialize(chennai_bb, augment=True)

################################################################################

if __name__ == "__main__":

    geo_info = init_using_files()
    #geo_info = init_using_elasticindex()

    header = [
        "tweet_mention",
        "mention_offsets",
        "geo_location",
        "geo_info_id",
        "geo_point"]

    for tweet in read_tweets():

        # remove non-ascii characters
        tweet = strip_non_ascii(tweet)

        print tweet

        rows = list()
        for x in lnex.extract(tweet):

            geo_point = {}

            try:
                # if we only have one geo_point then we are 100% certain of its
                # location and we don't need disambiguation
                if len(x[3]) == 1:
                    geo_point = geo_info[list(x[3])[0]]['geo_item']['point']
            except:
                pass

            row = x[0], x[1], x[2], x[3], geo_point
            rows.append(row)

        print "-" * 90
        print tabulate(rows, headers=header)
        print "-" * 90
