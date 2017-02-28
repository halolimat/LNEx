# LNEx: Location Name Extractor

LNEx extracts location names from targeted text streams. 

Following the steps which allows you to setup and start using LNEx.

### Querying OpenStreetMap Gazetteers
We will be using a ready to go elastic index of the whole [OpenStreetMap](http://www.osm.org) data provided by [komoot](http://www.komoot.de) as part of their [photon](https://photon.komoot.de/) open source geocoder ([project repo](https://github.com/komoot/photon)).
 - Download the full photon elastic index which is going to allow us to query OSM using a bounding box
   - wget -O - http://download1.graphhopper.com/public/photon-db-latest.tar.bz2 | bzip2 -cd | tar x
 - Now, start photon which starts the elastic index in the background
   - java -jar photon-0.2.7.jar


### Using LNEx

 - Clone this repository to your machine as follows:
   - clone https://github.com/halolimat/LNEx.git
  
 - Define your desired bounding box in main.py to build the custom OSM gazetteer (example Houston, TX bb):
 
 ```python
 houston_bb = [29.4778611958,-95.975189209,30.1463147381,-94.8889160156]
 ```
