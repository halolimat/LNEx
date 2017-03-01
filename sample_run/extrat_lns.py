import LNEx as lnex

def read_tweets():

    tweets_file = "Data/sample_tweets.txt"

    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()

    return tweets


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
