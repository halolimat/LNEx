"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import json
from tabulate import tabulate

import LNEx as lnex

from shapely.geometry import MultiPoint

################################################################################
################################################################################

def read_tweets():

    tweets_file = "_Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets

################################################################################

def init_using_files(dataset, capital_word_shape):

    with open("_Data/Cached_Gazetteers/"+dataset+"_geo_locations.json") as f:
        geo_locations = json.load(f)

    with open("_Data/Cached_Gazetteers/"+dataset+"_extended_words3.json") as f:
        extended_words3 = json.load(f)

    with open("_Data/Cached_Gazetteers/"+dataset+"_geo_info.json") as f:
        geo_info = json.load(f)

    lnex.initialize_using_files(geo_locations, extended_words3, capital_word_shape=capital_word_shape)

    return geo_info

################################################################################

def init_using_elasticindex(bb, cache, dataset, capital_word_shape):
    lnex.elasticindex(conn_string='localhost:9200', index_name="photon")

    geo_info = lnex.initialize( bb, augment=True,
                                    cache=cache,
                                    dataset_name=dataset,
                                    capital_word_shape=capital_word_shape)

    return geo_info

################################################################################

if __name__ == "__main__":

    bbs = {
        "chennai": [12.74, 80.066986084, 13.2823848224, 80.3464508057],
        "louisiana": [29.4563, -93.3453, 31.4521, -89.5276],
        "houston": [29.4778611958, -95.975189209, 30.1463147381, -94.8889160156]}

    dataset = "chennai"

    geo_info = init_using_files(dataset, capital_word_shape=False)
    #geo_info = init_using_elasticindex(bbs[dataset], cache=True, dataset=dataset, capital_word_shape=False)

    header = [
        "Spotted_Location",
        "Location_Offsets",
        "Geo_Location",
        "Geo_Point"]

    for tweet in read_tweets():

        rows = list()
        for output in lnex.extract(tweet):

            """
                output is a tuple of the following items:
                    1- location mention
                    2- mention offsets
                    3- matched gazetteer location
                    4- gaz location geo info id > a mapping to the mention metadata            
            """

            # dict of {'main': [ids], 'meta': [ids]} >
            #   main: is where the LN is the main mention, meta: where the LN appeared in the meta tags
            ids = output[3]

            geo_point = None

            if len(ids["main"]) > 0:
                # if only one geo_point then we are 100% certain of its location and we don't need disambiguation
                ids = ids["main"]

                # take only one of them (its your choice to choose more until we find a way to filter and disambiguate)
                geo_point = "main: " + str(geo_info[ids[0]]['geo_item']['point'])

            else:
                ids = ids["meta"]

                points = []
                for id in ids:
                    lat = geo_info[id]['geo_item']['point']["lat"]
                    lon = geo_info[id]['geo_item']['point']["lon"]
                    points.append((lat, lon))

                # find centroid of all points when the location name was found as the parent of other location names
                #   this is a default behavior for now, you can choose whatever behavior you would like.
                points = MultiPoint(points)

                lat = points.centroid.coords.xy[0][0]
                lon = points.centroid.coords.xy[1][0]

                geo_point = {"lat": lat, "lon": lon}

                geo_point = "meta: " + str(geo_point)

            row = output[0], output[1], output[2], geo_point
            rows.append(row)

        print "-" * 120
        print tabulate(rows, headers=header)
        print "#" * 120