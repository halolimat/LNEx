<!-- ###########################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################-->
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0) [![GitHub release](https://img.shields.io/badge/release-V1.1-orange.svg)]() [![Build Status](https://travis-ci.com/halolimat/LNEx.svg?token=Gg8N5fqoMjLGd4ehzd72&branch=master)](https://travis-ci.com/halolimat/LNEx)

<img src="LNEx_logo.png" align="left" alt="LNEx Logo" width="120"/>

<img src="http://knoesis.org/resources/images/hazardssees_logo_final.png" align="right" alt="Knoesis Hazards SEES Project Logo" width="90"/>

# Location Name Extractor

Extracts location names from targeted text streams.

---

Following are the steps which allows you to setup and start using LNEx.

## Querying OpenStreetMap Gazetteers  ##

We will be using a ready to go elastic index of the whole [OpenStreetMap](http://www.osm.org) data provided by [komoot](http://www.komoot.de) as part of their [photon](https://photon.komoot.de/) open source geocoder ([project repo](https://github.com/komoot/photon)). If you don't need to have the full index of OpenStreetMap then you might look for alternative options such as [Pelias OpenStreetMap importer](https://github.com/pelias/openstreetmap) provided by [Mapzen](https://www.mapzen.com/).

Using Photon might be a good idea for some users if they have enough space (~ 72 GB) and if they want to use LNEx for many streams along the way. If that sound like something you wanna do, follow the steps below:

 - Download the full photon elastic index which is going to allow us to query OSM using a bounding box

   ```sh
   wget -O - http://download1.graphhopper.com/public/photon-db-latest.tar.bz2 | bzip2 -cd | tar x
   ```

 - Now, start photon which starts the elastic index in the background as a service

   ```sh
   wget http://photon.komoot.de/data/photon-0.2.7.jar
   java -jar photon-0.2.7.jar
   ```

 - You should get the Port number information from the log of running the jar, similar to the following:

   ```
   [main] INFO org.elasticsearch.http - [Amelia Voght] bound_address {inet[/127.0.0.1:9201]},
   publish_address {inet[/127.0.0.1:9201]}
   ```

   - this means that elasticsearch is running correctly and listening on:

   ```
   localhost:9201
   ```
   - You can test the index by running the following command:
   ```sh
       curl -XGET 'http://localhost:9201/photon/place/_search/?size=5&pretty=1' -d '{
         "query": {
           "filtered": {
             "filter": {
               "geo_bounding_box" : {
                 "coordinate" : {
                   "top_right" : {
                     "lat" : 13.7940725231,
                     "lon" : 80.4034423828
                   },
                   "bottom_left" : {
                     "lat" : 12.2205755634,
                     "lon" : 79.0548706055
                   }
                 }
               }
             }
           }
         }
      }'
    ```

## Using LNEx ##

 - Clone this repository to your machine as follows:
    ```sh
    git clone https://github.com/halolimat/LNEx.git
    ```

 - Install LNEx as follows:
    ```sh
    cd LNEx
    python setup.py install
    ```

 - Now, you can start using LNEx to spot locations in tweets.
   ```python

   # Import LNEx inside your python script:   
   import LNEx as lnex

   # Define the elastic index connection string and index name
   lnex.elasticindex(conn_string='localhost:9200', index_name="photon")

   # Build the custom OSM gazetteer using your desired bounding box (e.g., for Chennai, India):
   chennai_bb = [12.74, 80.066986084, 13.2823848224, 80.3464508057]

   # Initialize LNEx using the defined bounding box. You can also choose to augment the gazetteer.
   lnex.initialize(chennai_bb, augment=True)

   # Now, we are ready to extract location names from the tweet
   lnex.extract("New avadi rd is closed #ChennaiFloods.")

   ```

 - The output is going to be a list of tuples of the following items:
    - Spotted_Location: is a substring of the tweet
    - Location_Offsets: are the start and end offsets of the Spotted_Location
    - Geo_Location: is the matched location name from the gazetteer
    - Geo_Info_IDs: are the ids of the geo information of the matched Geo_Locations


   ```python
   # output of the above code
   [('Chennai', (24, 31), 'chennai', [6568]),
    ('New avadi rd', (0, 12), u'new avadi road', [9568, 5060, 7238, 5063, 1896, 12722, 2820, 9375])]
   ```

 - You can also use the pre-written test run module 'pytest.py' to test LNEx. You can use LNEx by initializing it using the cached files in the '\_Data' folder or you can initialize it using the photon index after running it in the background.

 - Finally, LNEx is lightening fast and capable of tagging streams of texts, you can incorporate the [following code](https://github.com/tweepy/tweepy/blob/master/examples/streaming.py) to start streaming from Twitter (taking into consideration the spatial context) then define the bounding box that matches the spatial context established by your stream and start tagging the tweets.

## Citing ##

If you do make use of LNEx or any of its components please cite the following publication:

    @inproceedings{halolimatLNEx18,
      title={ Location Name Extraction from Targeted Text Streams using
              Gazetteer-based Statistical Language Models. },
      author={ Al-Olimat, Hussein S., Thirunarayan, Krishnaprasad,
               Shalin, Valerie and Sheth, Amit},
      booktitle={The 27th International Conference on Computational Linguistics (COLING 2018)},
      year={2018}
    }

We would also be very happy if you provide a link to the github repository:

    ... location name extractor tool (LNEx)\footnote{
        \url{https://github.com/halolimat/LNEx}
    }
