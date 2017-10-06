"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import json
import unicodedata
from tabulate import tabulate

import LNEx as lnex

################################################################################
################################################################################

def strip_non_ascii(s):
    if isinstance(s, unicode):
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

    lnex.elasticindex(conn_string='localhost:9200', index_name="photon")

    # chennai flood bounding box
    bb = [12.74, 80.066986084, 13.2823848224, 80.3464508057]

    return lnex.initialize(bb, augment=True)

################################################################################

if __name__ == "__main__":

    #geo_info = init_using_files()
    geo_info = init_using_elasticindex()

    header = [
        "Spotted_Location",
        "Location_Offsets",
        "Geo_Location",
        "Geo_Info_IDs"
        "Geo_Point"]

    for tweet in read_tweets():

        # remove non-ascii characters
        tweet = strip_non_ascii(tweet)

        print tweet

        #tweet = "New avadi rd is closed #ChennaiFloods."

        rows = list()
        for x in lnex.extract(tweet):

            geo_point = {}

            try:
                # if we only have one geo_point then we are 100% certain of its
                # location and we don't need disambiguation
                if len(x[3]) == 1:
                    geo_point = geo_info[list(x[3])[0]]['geo_item']['point']
            except KeyError, e:
                pass

            row = x[0], x[1], x[2], x[3], geo_point
            rows.append(row)

        print "-" * 120
        print tabulate(rows, headers=header)
        print "#" * 120
