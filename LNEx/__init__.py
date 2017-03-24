"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import core
import osm_gazetteer

################################################################################
################################################################################

def initialize_using_files(geo_locations, extended_words3):
    core.initialize(geo_locations, extended_words3)

################################################################################

def initialize(bb, augment=True):

    # retrieve the records from OSM based on the passed bb
    geo_locations, geo_info, extended_words3 = \
            osm_gazetteer.build_bb_gazetteer(bb, augment)

    # initialize LNEx using the retrieved (possible augmented) location names
    core.initialize(geo_locations, extended_words3)

    return geo_info

################################################################################

def extract(tweet):

    return core.extract(tweet)

################################################################################

# sets the elasticindex connection string and index name where OSM is indexed
def elasticindex(conn_string, index_name):

    osm_gazetteer.set_elasticindex_conn(conn_string, index_name)
