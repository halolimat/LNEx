<!-- ###########################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################-->
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0) [![GitHub release](https://img.shields.io/badge/release-V1.1-orange.svg)]() [![Build Status](https://travis-ci.com/halolimat/LNEx.svg?token=Gg8N5fqoMjLGd4ehzd72&branch=master)](https://travis-ci.com/halolimat/LNEx)

<img src="LNEx_logo.png" align="left" alt="LNEx Logo" width="120"/>

<!-- <img src="http://knoesis.org/resources/images/hazardssees_logo_final.png" align="right" alt="Knoesis Hazards SEES Project Logo" width="90"/>-->

# Location Name Extractor

Extracts location names from targeted text streams. [[Paper](https://www.aclweb.org/anthology/C18-1169), [Poster](https://link.hussein.space/LNEx-Poster)]

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

 - Now, start photon which starts the elastic index in the background as a service. You need to get the latest jar file from the releases at https://github.com/komoot/photon/releases. For example, the current latest version is 0.3.2, you can get the latest jar and run it as follows:

   ```sh
   wget https://github.com/komoot/photon/releases/download/0.3.2/photon-0.3.2.jar
   java -jar photon-0.3.2.jar
   ```

 - You can now test the running index by running the following command (9200 is the default port number, might be different in your system if the port is occupied by another application):
   ```sh
   curl -XGET 'http://localhost:9200/photon/'
   ```

## Using LNEx ##

 - Clone this repository to your machine as follows (you should add the branch name if you are cloning a specific branch):
    ```sh
    git clone https://github.com/halolimat/LNEx.git
    ```
 - Make sure to use Python 3.6+.

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

You can fill out the following [Form](https://link.hussein.space/LNEx-Form) to get the full dataset. Alternatively, you can get a subset of the dataset from [this folder](https://link.hussein.space/LNEx-Data), which only contains 150 tweets.

*We would like to thank Xuke Hu of dlr.de for his contributions to fix some errors in the labels.*

## Notes ##

Since LNEx relies on OSM gazetteers for extraction, the performance of the tool will be affacted by the version of the data. The performance of the tool reported in the paper used the Photon index with the following properties:
   - "number" : "1.7.0",
   - "build_hash" : "929b9739cae115e73c346cb5f9a6f24ba735a743",
   - "build_timestamp" : "2015-07-16T14:31:07Z"

## Debugging ##

There are a few things you need to make sure of before you get Photon to work well with LNEx.
- You should have the latest photon jar file (see above).
- Your elasticsearch-dsl in python should be compatible with the Photon version you downloaded. You should first check the version of elasticsearch by running `curl -XGET 'http://localhost:9200'`, you will find the version number under `version/number`.
- The current version of elasticsearch using by Photon is `5.5.0`, so we should get the compatible elasticsearch-dsl to use it in our Python code. You can do that by visiting [this page](https://elasticsearch-dsl.readthedocs.io/en/latest/). You will find the compatible version under `The recommended way to set your requirements ...`. In the case of `5.5.0`, the compatible version is `elasticsearch-dsl-5.4.0`, so we install it as so `pip install "elasticsearch-dsl>=5.0.0,<6.0.0"`.

**Photon Index Issue**

There is an issue with the elasticsearch index of Photon 0.3.2, so you need to do delete all files in the following directory `/photon_data/elasticsearch/modules/lang-painless/` in order to get it running before you execute `java -jar photon-0.3.2.jar`. For more info, see the following: https://github.com/komoot/photon/issues/427

## Licenses ##

This work is licensed under AGPL-3.0 and CreativesForGood licenses. A copy of the first license can be found in this repository. The other license can be found over this link [C4G License](https://github.com/halolimat/CreativesForGoodLicense).

<p float="left">
  <img src="https://upload.wikimedia.org/wikipedia/commons/0/06/AGPLv3_Logo.svg" alt="GPLv3 Logo" width="70" />
  <img src="https://github.com/halolimat/CreativesForGoodLicense/raw/master/CreativesForGoodLogo2.png" alt="CreativesForGood Logo" width="120" style="margin-left: 10px;" /> 
</p>

## Citing ##

If you do make use of LNEx or any of its components please cite the following publication:

    Hussein S. Al-Olimat, Krishnaprasad Thirunarayan, Valerie Shalin, and Amit Sheth. 2018. 
    Location Name Extraction from Targeted Text Streams using Gazetteer-based Statistical Language Models. 
    In Proceedings of the 27th International Conference on Computational Linguistics (COLING 2018), 
    pages 1986–1997. Association for Computational Linguistics.

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
