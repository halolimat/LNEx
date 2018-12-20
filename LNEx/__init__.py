"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

import os, json
import elasticsearch

from . import core
from . import osm_gazetteer

################################################################################
################################################################################

__all__ = [ 'initialize_using_files',
            'initialize',
            'extract',
            'elasticindex']

################################################################################

def initialize_using_files(geo_locations, extended_words3, capital_word_shape=False):
    """Initialize LNEx using files in _Data without using the elastic index"""

    core.initialize(geo_locations, extended_words3, capital_word_shape)

################################################################################

def initialize(bb, augmentType, cache, dataset_name, capital_word_shape=False):
    """Initialize LNEx using the elastic index"""

    geo_locations = None
    geo_info = None
    extended_words3 = None

    while geo_info is None:
        try:
            # retrieve the records from OSM based on the passed bb
            geo_locations, geo_info, extended_words3 =  osm_gazetteer.build_bb_gazetteer(bb, augmentType)
        except elasticsearch.exceptions.ConnectionTimeout:
            pass

    # initialize LNEx using the retrieved (possible augmented) location names
    core.initialize(geo_locations, extended_words3, capital_word_shape)

    if cache:

        folder_abs_path = os.path.abspath(os.path.join(os.path.dirname( __file__),
                            '..', "_Data", "Cached_Gazetteers"))

        if not os.path.exists(folder_abs_path):
            os.makedirs(folder_abs_path)

        with open(folder_abs_path+"/"+dataset_name+"_geo_locations.json", "w") as f:
            json.dump(geo_locations, f)
        with open(folder_abs_path+"/"+dataset_name+"_geo_info.json", "w") as f:
            json.dump(geo_info, f)
        with open(folder_abs_path+"/"+dataset_name+"_extended_words3.json", "w") as f:
            json.dump(extended_words3, f)

    return geo_info

################################################################################

def extract(tweet):
    """Extracts location names from a tweet text and return a list of tuples"""

    return core.extract(tweet)

################################################################################

def elasticindex(conn_string, index_name):
    """sets the elasticindex connection string and index name where the
    gazetteer data resides"""

    osm_gazetteer.set_elasticindex_conn(conn_string, index_name)
