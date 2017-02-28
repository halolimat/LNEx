# LNEx: Location Name Extractor #

LNEx extracts location names from targeted text streams.

---

Following are the steps which allows you to setup and start using LNEx.

## Querying OpenStreetMap Gazetteers  ##

We will be using a ready to go elastic index of the whole [OpenStreetMap](http://www.osm.org) data provided by [komoot](http://www.komoot.de) as part of their [photon](https://photon.komoot.de/) open source geocoder ([project repo](https://github.com/komoot/photon)).
 - Download the full photon elastic index which is going to allow us to query OSM using a bounding box
   - wget -O - http://download1.graphhopper.com/public/photon-db-latest.tar.bz2 | bzip2 -cd | tar x
 - Now, start photon which starts the elastic index in the background
   - java -jar photon-0.2.7.jar

If you don't need to have the full index of OpenStreetMap then you might look for alternative options such as [Pelias OpenStreetMap importer](https://github.com/pelias/openstreetmap) provided by [Mapzen](https://www.mapzen.com/).

## Using LNEx ##

 - Clone this repository to your machine as follows:
   - git clone https://github.com/halolimat/LNEx.git

 - Install LNEx as follows:
   - cd LNEx
   - python setup.py install

 - Install all the requirements and test your installation and the elasticsearch index:
   - ./Makefile

Now, you can start using LNEx to spot locations in some tweets from the 2015 Chennai Flood tweets.

 - Define your desired bounding box in main.py to allow LNEx to build the custom OSM gazetteer (e.g., for Chennai, India):

   ```python

   # chennai flood bounding box
   chennai_bb = [  12.74,80.066986084,
                   13.2823848224,80.3464508057 ]

    # retrieve all OSM records inside the given BB then augment and filter the gazetteer
    gazetteer = build_gazetteer(chennai_bb)

    # build a language model from the custom gazetteer for spotting
    lm = build_lm(gazetteer)

   ```
 - Now, we need to pass the tweets to LNEx to start extracting locations from them. LNEx is lightening fast and capable of tagging streams of data (you can incorporate the [following code](https://github.com/tweepy/tweepy/blob/master/examples/streaming.py) into LNEx). Following is a simple example of reading from a file and passing the tweets to LNEx for tagging:
   ```python
    # read tweets from file to list
    with open(filename) as f:
        tweets = f.read().splitlines()

    for tweet in tweets:
        extract_locations(tweet, lm)
   ```
---

## Citing ##

If you do make use of LNEx or any of its components please cite the following publication:

    @inproceedings{halolimatLNEx17,
      title={ Location Name Extraction from Targeted Text Streams using
              a Gazetteer-based Statistical Language Model. },
      author={ Al-Olimat, Hussein S. and Thirunarayan, Krishnaprasad
               and Shalin, Valerie and Sheth, Amit},
      booktitle={IJCAI},
      volume={7},
      pages={2733--2739},
      year={2017}
    }

We would also be very happy if you link to our project page:

    ... location name extractor tool (LNEx)\footnote{
        \url{https://github.com/halolimat/LNEx}
    }
