# LNExAPI - Client

LNExAPI Client is a Python 3 package that includes functions to interact with the LNExAPI Server. Installing the LNExAPI Client is simple. Installation and example use is shown below:

### Installation

* Navigate to the client/LNExAPI folder
* Issue: `python setup.py install`

### Example Use 

Example below shows how to create a zone and extract locations.

```python
from LNExAPI import LNExAPI

def displayResults(results):
  for result in results:
    print("Matches for:",result['text'])
    for entity in result['entities']:
      print("[ ]-->",entity['match'])
      for location in entity['locations']:
        print("   [ ]-->",str(location['coordinate']['lat'])+","+str(location['coordinate']['lon']))

lnex = LNExAPI(key="168ba4d297a8c64a03", host="http://127.0.0.1/") #REPLACE WITH YOUR USER KEY AND HOST
lnex.initZone([-84.6447033333,39.1912856591,-83.2384533333,40.0880515857],"dayton")
print("Zone Dayton is being initialized...")
lnex.pollZoneReady("dayton") #WAITS UNTIL ZONE IS INIT/READY

text=[
  "Your text goes here:",
  "A list of text in which locations will be searched for...",
  "A list of the same size will be returned once you execute a doBulkExtract on the text list",
  "Each item in the returned list will be a list of the entities that matched",]

print("Extracting locations from Dayton Zone...")
result_token,results=lnex.pollFullBulkExtract("dayton",text)
displayResults(results)
```
Other functions that can be useful are documented in the [LNExAPI.py](client/LNExAPI/LNExAPI/LNExAPI.py) class file.
### LNEx-Deployment

[Back to main Readme](README.md)