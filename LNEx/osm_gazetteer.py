import json, sys, os, re
from collections import defaultdict
from json import JSONEncoder

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from operator import itemgetter
from itertools import groupby

import gaz_augmentation_and_filtering

def search_index(bb):
    es = Elasticsearch()

    connections.create_connection(hosts=['130.108.85.186:9200'], timeout=20)

    phrase_search = [Q({"filtered" : {
                  "filter" : {
                    "geo_bounding_box" : {
                      "coordinate" : {
                        "bottom_left" : {
                          "lat" : bb[0],
                          "lon" : bb[1]
                        },
                        "top_right" : {
                          "lat" : bb[2],
                          "lon" : bb[3]
                        }
                      }
                    }
                  },
                  "query": {
                    "match_all": {}
                    }
                  }
    })]

    # to search with a scroll
    e_search = Search(index="photon_v1").query(Q('bool', must=phrase_search))

    try:
        res = e_search.scan()
    except:
        pass

    return res


def get_text(obj):

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
            except:
                return obj

def build_bb_gazetteer(bb):

    # accepted fields as location names
    location_fields = [ "city", "country",
                        "name", "state", "street"]

    raw_names = list()

    for match in search_index(bb):

        for key in dir(match):

            if key in location_fields:
                try:
                    text = get_text(match[key])

                    raw_names.append(text)

                except:
                    print "exception at record # ", count
                    print get_text(match[key])
                    raise


    return gaz_augmentation_and_filtering.run(raw_names)

if __name__ == "__main__":

    chennai_bb = [  12.74,80.066986084,
                    13.2823848224,80.3464508057 ]

    unique, all, extended_words3 = build_bb_gazetteer(chennai_bb)

    for x in unique:
        print x

    for x in all:
        print x
