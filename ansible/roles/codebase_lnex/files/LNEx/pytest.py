import json, re
from shapely.geometry import MultiPoint

import sys 
sys.path.append("LNEx")
import LNEx as lnex
import redis
from DRDB import DRDB

db=DRDB("/var/local/LNEx.db")
args=sys.argv

name=args[1]
campaignInfo=db.get_campaign(name)
if campaignInfo:
  bb=campaignInfo[0][2]
  bb = [ float(n) for n in bb[1:-1].split(",") ]
  print(bb)
text=args[2]




def read_tweets():
    tweets_file = "_Data/sample_tweets.txt"
    # read tweets from file to list
    with open(tweets_file) as f:
        tweets = f.read().splitlines()
    return tweets

def init_using_elasticindex(bb, cache, augmentType, dataset, capital_word_shape):
    lnex.elasticindex(conn_string='130.108.86.153:9201', index_name="photon")

    geo_info = lnex.initialize( bb, augmentType=augmentType,
                                    cache=cache,
                                    dataset_name=dataset,
                                    capital_word_shape=capital_word_shape)
    return geo_info


bbs = { "chennai": [12.74, 80.066986084, 13.2823848224, 80.3464508057],
        "louisiana": [29.4563, -93.3453, 31.4521, -89.5276],
        "houston": [29.4778611958, -95.975189209, 30.1463147381, -94.8889160156],
        "midwest": [37.66, -91.66, 42.87, -80.64],
        "ohio": [38.58, -84.85, 41.88, -80.51],
        "wyoming": [41.03,-111.03,44.98,-104.04],
        "dayton-cinn": [39.04,-84.73,40.06,-83.89],
        "alabama": [30.16,-88.45,35.1,-85.22],
        "USA": [29.58,-125.16,49.15,-67.2]}

bbs[name] = bb


dataset = name

import math
R=6371
PI=3.14159265
X1=math.fabs(math.cos(math.radians(bbs[dataset][2]))-math.cos(math.radians(bbs[dataset][0])))
X2=math.fabs(bbs[dataset][3]-bbs[dataset][1])
A=(PI/180.0)*math.pow(R,2)*X1*X2
print("KM:",A)

#import redis
#r = redis.Redis(host='DR-redis')

geo_info = init_using_elasticindex(bbs[dataset], cache=False, augmentType="HP", 
                                   dataset=dataset, capital_word_shape=False)

o=lnex.extract(text)
print(o[0], o[1], o[2], o[3]["main"])
#for tweet in read_tweets():
#    for output in lnex.extract(tweet):
#        print(output[0], output[1], output[2], output[3]["main"])
#    print("#"*50)