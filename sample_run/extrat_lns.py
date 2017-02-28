
tweets_file = "Data/sample_tweets.txt"

# read tweets from file to list
with open(tweets_file) as f:
    tweets = f.read().splitlines()

for tweet in tweets:
    #extract_locations(tweet, lm)

    print tweet
