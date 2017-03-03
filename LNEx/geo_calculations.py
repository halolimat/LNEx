from geopy.distance import vincenty

def get_distance_between_latlon_points(x1, x2):

    '''     ---------------
            |           + |
            |          lat|
            |           - |
            ---------------
              -  long  +         '''

    return vincenty(x1, x2).km


def is_bb_acceptable(bb):

    # south east point from the two sw and ne points
    sw = (bb[0], bb[1])
    ne = (bb[2], bb[3])
    se = (bb[0], bb[3])

    width = get_distance_between_latlon_points(sw,se)

    height = get_distance_between_latlon_points(ne,se)

    area = (width*height)/1000000

    # larger than the state of Texas
    if area > 1.6:
        return False

    else:
        return True


if __name__ == "__main__":

    texas_bb = [25.8371638,-106.6456461,36.5007041,-93.5080389]

    print is_bb_acceptable(texas_bb)
