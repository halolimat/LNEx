import prepare_osm_gazetteer


def init():
    return "initalized"

def build_gazetteer(bb):
    return osm_gazetteer.build_bb_gazetteer(bb)

def build_lm(gazetteer):
    return gazetteer

def extract_locations(tweet, lm):
    return tweet, lm
