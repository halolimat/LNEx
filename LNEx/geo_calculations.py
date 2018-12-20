"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

from geopy.distance import vincenty

################################################################################
################################################################################

__all__ = [ 'get_distance_between_latlon_points',
            'is_bb_acceptable']

################################################################################

def get_distance_between_latlon_points(x1, x2):
    '''Calculates the distance between two geo points in km.

            ---------------
            |           + |
            |          lat|
            |           - |
            ---------------
              -  long  +         '''

    return vincenty(x1, x2).km

################################################################################

def is_bb_acceptable(bb):
    '''Checks if the bounding box used is at most as big as Texas State'''

    # south east point from the two sw and ne points
    sw = (bb[0], bb[1])
    ne = (bb[2], bb[3])
    se = (bb[0], bb[3])

    width = get_distance_between_latlon_points(sw, se)

    height = get_distance_between_latlon_points(ne, se)

    area = (width * height) / 1000000

    # larger than the state of Texas
    if area > 1.6:
        return False

    else:
        return True

################################################################################

if __name__ == "__main__":

    texas_bb = [25.8371638, -106.6456461, 36.5007041, -93.5080389]

    print(is_bb_acceptable(texas_bb))
