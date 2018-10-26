<!-- ###########################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################-->
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0) [![GitHub release](https://img.shields.io/badge/release-V1.1-orange.svg)]() [![Build Status](https://travis-ci.com/halolimat/LNEx.svg?token=Gg8N5fqoMjLGd4ehzd72&branch=master)](https://travis-ci.com/halolimat/LNEx)

<img src="LNEx_logo.png" align="left" alt="LNEx Logo" width="120"/>

<img src="http://knoesis.org/resources/images/hazardssees_logo_final.png" align="right" alt="Knoesis Hazards SEES Project Logo" width="90"/>

# Location Name Extractor

Extracts location names from targeted text streams. [[Paper](https://arxiv.org/pdf/1708.03105.pdf), [Poster](https://link.hussein.space/LNEx-Poster)]

---

## How do you pronounce LNEx?
Le-N-x

---

Following are the steps which allows you to setup and start using LNEx.

## Querying OpenStreetMap Gazetteers  ##

We will be using a ready to go elastic index of the whole [OpenStreetMap](http://www.osm.org) data (~ 108 GB) provided by [komoot](http://www.komoot.de) as part of their [photon](https://photon.komoot.de/) open source geocoder ([project repo](https://github.com/komoot/photon)). Follow the steps below to get Photon running in your system:

 - Download the full photon elastic index which is going to allow us to query OSM using a bounding box

   ```sh
   wget -O - http://download1.graphhopper.com/public/photon-db-latest.tar.bz2 | pbzip2 -cd | tar x
   ```

 - Now, start photon which starts the elastic index in the background as a service

   ```sh
   wget https://github.com/komoot/photon/releases/download/0.3.0/photon-0.3.0.jar
   java -jar photon-0.3.0.jar
   ```

 - You should get the Port number information from the log of running the jar, similar to the following:

   ```
   ... bound_address {inet[/127.0.0.1:9201]} ... publish_address {inet[/127.0.0.1:9201]}
   ```

   - this means that elasticsearch is running correctly and listening on:

   ```
   localhost:9201
   ```
   - You can test the index by running the following command:
   ```sh
       curl -XGET 'http://localhost:9201/photon/'
   ```

## Using LNEx ##

 - Clone this repository to your machine as follows (you should add the branch name if you are cloning a specific branch):
    ```sh
    git clone https://github.com/halolimat/LNEx.git
    ```

 - Follow the example in pytest.py or pytest.ipy in order to use LNEx. You can use LNEx by initializing it using the cached files in the '\_Data' folder or you can initialize it using the photon index after running it in the background as shown before.

 - The output is going to be a list of tuples of the following items:
    - Spotted_Location: is a substring of the tweet
    - Location_Offsets: are the start and end offsets of the Spotted_Location
    - Geo_Location: is the matched location name from the gazetteer
    - Geo_Info_IDs: are the ids of the geo information of the matched Geo_Locations

   ```python
   # output of the tool:
   [('Chennai', (24, 31), 'chennai', [6568]),
    ('New avadi rd', (0, 12), u'new avadi road', [9568, 5060, 7238, 5063, 1896, 12722, 2820, 9375])]
   ```

 - Finally, LNEx is lightening fast and capable of tagging streams of texts, you can incorporate the [following code](https://github.com/tweepy/tweepy/blob/master/examples/streaming.py) to start streaming from Twitter (taking into consideration the spatial context) then define the bounding box that matches the spatial context established by your stream and start tagging the tweets.

## Dataset ##

**Tagged Location Names in Targeted Social Media Streams** dataset

This dataset contains 4500 annotated tweets 1500 tweets from each of three Twitter streams (i.e., Chennai 2015, Louisiana 2016, and Houston 2016 floods). They were tagged using Brat tool recording the start and end character offsets of each mention with a given location category, i.e., inLoc, outLoc, and ambLoc, as mentioned in the LNEx paper.

You can fill out the following [Form](https://link.hussein.space/LNEx-Form) to the get the full dataset. Alternatively, you can get a subset of the dataset from [this folder](https://link.hussein.space/LNEx-Data), which only contains 150 tweets.

## Citing ##

If you do make use of LNEx or any of its components please cite the following publication:

    Hussein S. Al-Olimat, Krishnaprasad Thirunarayan, Valerie Shalin, and Amit Sheth. 2018. 
    Location Name Extraction from Targeted Text Streams using Gazetteer-based Statistical Language Models. 
    In Proceedings of the 27th Internationl Conference on Computational Linguistics (COLING 2018), 
    pages 700–710. Association for Computational Linguistics.

    @InProceedings{C18-1169,
      author = "Al-Olimat, Hussein S.
               and Thirunarayan, Krishnaprasad
               and Shalin, Valerie
               and Sheth, Amit",
      title = "Location Name Extraction from Targeted Text Streams using Gazetteer-based Statistical Language Models",
      booktitle = "Proceedings of the 27th International Conference on Computational Linguistics",
      year = "2018",
      publisher = "Association for Computational Linguistics",
      pages = "1986--1997",
      location = "Santa Fe, New Mexico, USA",
      url = "http://aclweb.org/anthology/C18-1169"
    }


We would also be very happy if you provide a link to the github repository:

    ... location name extractor tool (LNEx)\footnote{
        \url{https://github.com/halolimat/LNEx}
    }
