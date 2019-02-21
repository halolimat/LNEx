# LNExAPI - Client

LNExAPI Client is a Python 3 package that includes functions to interact with the LNExAPI Server. Installing the LNExAPI Client is simple. Installation and example use is shown below:

### Installation

* Navigate to the client/LNExAPI folder
* Issue: `python setup.py install`

### Example Use 

Open a Python3 interpreter and issue the following commands.

```
>>> from LNExAPI import LNExAPI
>>> lnex = LNExAPI("168ba4d297a8c64a03")  #REPLACE WITH YOUR USER KEY
>>> lnex.initZone([-84.6447033333,39.1912856591,-83.2384533333,40.0880515857],"dayton")
>>> lnex.zoneReady("dayton")
>>> text=[
  "Your text goes here:",
  "A list of text in which locations will be searched for...",
  "A list of the same size will be returned once you execute a doBulkExtract on the text list",
  "Each item in the returned list will be a list of the entities that matched",
]
>>> o=lnex.doBulkExtract("dayton",text)
>>> for r in o:
...   print(r)
>>> exit()
```
Other functions that can be useful are documented in the [LNExAPI.py](client/LNExAPI/LNExAPI/LNExAPI.py) class file.
### DisasterRecord-Deployment

[Back to main Readme](README.md)