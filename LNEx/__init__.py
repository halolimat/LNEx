"""
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
"""


import core
import osm_gazetteer


def initialize_using_files(geo_locations, extended_words3):
    core.initialize(geo_locations, extended_words3)

def initialize(bb):

    geo_locations, geo_info, extended_words3 = \
            osm_gazetteer.build_bb_gazetteer(bb)

    core.initialize(geo_locations, extended_words3)

def extract(tweet):

    return core.extract(tweet)

def set_connection_string(conn_str):

    osm_gazetteer.set_connection_string(conn_str)
