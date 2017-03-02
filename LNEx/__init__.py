import osm_gazetteer


def init():
    return "initalized"

def build_gazetteer(bb):

    osm_gazetteer.set_host_port('130.108.85.186:9200')

    return osm_gazetteer.build_bb_gazetteer(bb)

def build_lm(gazetteer):
    return gazetteer

def extract_locations(tweet, lm):
    return tweet, lm
