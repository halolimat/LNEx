"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import json
from collections import defaultdict

from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections

import geo_calculations
import gaz_augmentation_and_filtering

################################################################################
################################################################################

__all__ = [ 'set_elasticindex_conn',
            'search_index',
            'extract_text',
            'build_bb_gazetteer']

################################################################################
connection_string = ""
index_name = ""
################################################################################

def set_elasticindex_conn(cs, inn):
    '''Sets the connection string and index name for the elastic index

    connection_string: (e.g, localhost:9200)
    index_name: (e.g., photon) '''


    global connection_string
    global index_name

    connection_string = cs
    index_name = inn

################################################################################

def search_index(bb):
    '''Retrieves the location names from the elastic index using the given
    bounding box'''


    if connection_string == '' or index_name == '':

        print("\n###########################################################")
        print("Global ERROR: Elastic host and port or index name not defined")
        print("#############################################################\n")
        exit()

    if not geo_calculations.is_bb_acceptable(bb) or bb[0] > bb[2] or bb[1] > bb[3]:

        print("\n##########################################################")
        print("Global ERROR: Bounding Box is too big, choose a smaller one!")
        print("############################################################\n")
        exit()

    connections.create_connection(hosts=[connection_string], timeout=60)

    query = { "bool": {
                "must": {
                  "match_all": {}
                },
                "filter": {
                  "geo_bounding_box": {
                    "coordinate": {
                      "bottom_left": {
                        "lat": bb[0],
                        "lon": bb[1]
                      },
                      "top_right": {
                        "lat": bb[2],
                        "lon": bb[3]
                      }
                    }
                  }
                }
              }
            }


    phrase_search = [Q(query)]

    #to search with a scroll
    e_search = Search(index=index_name).query(Q('bool', must=phrase_search))

    try:
        res = e_search.scan()
    except BaseException:
        raise

    return res

################################################################################

def extract_text(obj):
    '''Extracts a location name from the different json fields in order
    giving the priority to (en) then (default), and so on. '''


    keys = dir(obj)

    if len(keys) == 1:
        return obj[keys[0]]

    else:
        if "en" in keys:
            return obj["en"]
        elif "default" in keys:
            return obj["default"]
        elif "reg" in keys:
            return obj["reg"]
        elif "old" in keys:
            return obj["old"]
        elif "alt" in keys:
            return obj["alt"]
        elif "loc" in keys:
            return obj["loc"]
        elif "int" in keys:
            return obj["int"]
        else:
            try:
                return obj[keys[0]]
            except BaseException:
                return obj

################################################################################

def build_bb_gazetteer(bb, augmentType):
    '''Builds the gazetteer of a bounding box and agument it in case
    augmentation is activated. '''

    assert augmentType in ["FULL", "FILTER", "HP", "NA"]

    # accepted fields as location names
    location_fields = ["city", "country",
                       "name", "state", "street"]

    geo_info = defaultdict()
    geo_locations = defaultdict(lambda: defaultdict(list))

    _id = 0

    for match in search_index(bb):

        _id += 1

        keys = dir(match)

        geo_item = defaultdict()

        if "coordinate" in keys:
            geo_item["point"] = {str(x): match["coordinate"][x] for x in match["coordinate"]}
        if "extent" in keys:
            top_left = match["extent"]["coordinates"][0]
            bottom_right = match["extent"]["coordinates"][1]

            geo_item["extent"] = {
                "top_left": {"lat": top_left[1], "lon": top_left[0]},
                "bottom_right": {"lat": bottom_right[1], "lon": bottom_right[0]}
            }

        #######################################################################

        for key in dir(match):

            if key in location_fields:

                try:
                    text = extract_text(match[key])

                    if key == "name":
                        # mapping a location name to its geo-info
                        geo_locations[text]["main"].append(str(_id))

                        geo_info[str(_id)] = {"name": text,
                                         "geo_item": geo_item}

                    else:
                        # if the location name is taken from the metadata
                        #geo_locations[text] = list()
                        geo_locations[text]["meta"].append(str(_id))

                except BaseException:
                    print (extract_text(match[key]))
                    raise

    if augmentType=="FULL": # Full augmentation and filtering as in COLING 2018 publication
        # 'pullapuram road': set([493])
        new_geo_locations, extended_words3 = gaz_augmentation_and_filtering.augment(geo_locations)

    elif augmentType=="FILTER": # None
        new_geo_locations = gaz_augmentation_and_filtering.filter_geo_locations(geo_locations)
        extended_words3 = gaz_augmentation_and_filtering.get_extended_words3(list(new_geo_locations.keys()))

    elif augmentType=="HP": # High Precision Filtering
        new_geo_locations = gaz_augmentation_and_filtering.high_precision_filtering(geo_locations)
        extended_words3 = gaz_augmentation_and_filtering.get_extended_words3(list(new_geo_locations.keys()))

    elif augmentType=="NA":
        new_geo_locations = dict()
        for x in geo_locations:
            new_geo_locations[x.lower()] = geo_locations[x]
        extended_words3 = gaz_augmentation_and_filtering.get_extended_words3(list(new_geo_locations.keys()))

    # for serialization
    geo_info = dict(geo_info)

    for ln in new_geo_locations:
        new_geo_locations[ln] = {"main": list(new_geo_locations[ln]["main"]),
                                 "meta": list(new_geo_locations[ln]["meta"])}

    return new_geo_locations, geo_info, extended_words3

################################################################################

if __name__ == "__main__":

    bb = [41.6187434973, -83.7106928844, 41.6245055116, -83.7017216664]

    # connection_string = '130.108.85.186:9200'
    # index_name = "photon_v1"

    connection_string = "localhost:9200"
    index_name = "photon"

    set_elasticindex_conn(connection_string, index_name)

    geo_locations, geo_info, extended_words3 = build_bb_gazetteer(bb)

    print(json.dumps(dict(geo_locations), indent=2))
