import LNEx as lnex

def read_tweets():

    tweets_file = "_Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets


def start_using_files():

    # chennai flood bounding box
    chennai_bb = [  12.74,  80.066986084,
                    13.2823848224,  80.3464508057 ]

    ##############################################

    with open("_Data/chennai_geo_locations.json") as f:
        geo_locations = json.load(f)
    with open("_Data/chennai_geo_info.json") as f:
        geo_info = json.load(f)
    with open("_Data/chennai_extended_english_words.json") as f:
        extended_longlist_stopwords = json.load(f)

    env = init_env(geo_locations, extended_longlist_stopwords)

    tweet = "I am at new avadi rd, chennai, mambalam #chennaiflood #newavadiroad"

    # set of > (tweet_mention, offsets, geo_location)
    toponyms_in_tweet = extract(env, tweet)

    header = ["tweet_mention", "mention_offsets", "geo_location", "geo_info_id"]

    rows = list()
    for x in toponyms_in_tweet:
        row = x[0], x[1], x[2], geo_locations[x[2]]
        rows.append(row)

    print "-" * 90
    print tabulate(rows, headers=header)
    print "-" * 90

    print getsize(env)


def start_using_elastic_index():

    # chennai flood bounding box
    chennai_bb = [  12.74,  80.066986084,
                    13.2823848224,  80.3464508057 ]

    osm_gazetteer.set_connection_string('130.108.85.186:9200')

    geo_locations, geo_info, extended_longlist_stopwords = osm_gazetteer.build_bb_gazetteer(chennai_bb)

    env = init_env(geo_locations, extended_longlist_stopwords)

    tweet = "I am at new avadi rd, chennai, mambalam #chennaiflood #newavadiroad"

    # set of > (tweet_mention, offsets, geo_location)
    toponyms_in_tweet = extract(env, tweet)

    header = ["tweet_mention", "mention_offsets", "geo_location", "geo_info_id"]

    rows = list()
    for x in toponyms_in_tweet:
        row = x[0], x[1], x[2], geo_locations[x[2]]
        rows.append(row)

    print "-" * 90
    print tabulate(rows, headers=header)
    print "-" * 90


if __name__ == "__main__" :

    # chennai flood bounding box
    chennai_bb = [  12.74,  80.066986084,
                    13.2823848224,  80.3464508057 ]

    # retrieve all OSM records inside the given BB then augment and filter the gazetteer
    #
    gaz_unique_names, gaz_all_names = lnex.build_gazetteer(chennai_bb)

    # build a language model from the custom gazetteer for spotting
    lm = lnex.build_lm(gazetteer)

    for tweet in read_tweets():

        print tweet

        # extract location names and return them in a list with their character offsets
        print lnex.extract_locations(tweet, lm)
