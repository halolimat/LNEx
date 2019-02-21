import json, re
from shapely.geometry import MultiPoint

import sys 
sys.path.append("LNEx")
import LNEx as lnex
import redis
from DRDB import DRDB

db=DRDB("/var/local/LNEx.db")
args=sys.argv

bb=None

name=args[1]
zoneInfo=db.get_zone(name)
if zoneInfo:
  bb=zoneInfo[0][2]
  bb = [ float(n) for n in bb[1:-1].split(",") ]
  print(bb)
text=" ".join(args[2:])
print(text)

def zones():
  o = {}
  for area in areas:
    o[area] = [
      areas[area][1],
      areas[area][0],
      areas[area][3],
      areas[area][2]]
  return o

def calcArea():
  import math
  R=6371
  PI=3.14159265
  X1=math.fabs(math.cos(math.radians(bbs[dataset][2]))-math.cos(math.radians(bbs[dataset][0])))
  X2=math.fabs(bbs[dataset][3]-bbs[dataset][1])
  A=(PI/180.0)*math.pow(R,2)*X1*X2
  print("EST KM^2:",A)

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

areas = { 
  "daytonArea": [-84.625426,39.355459,-83.687469,40.091652],
  "NYCsmall": [-74.1108,40.7275,-73.9954,40.8345],}

if bb:
  pass
elif name in bbs:
  bb=bbs[name]
elif name in zones():
  bb=zones()[name]
else:
  print("area name not found")
  sys.exit()

bbs[name] = bb
dataset = name

calcArea()

geo_info = init_using_elasticindex(bbs[dataset], cache=False, augmentType="HP", 
                                   dataset=dataset, capital_word_shape=False)

extracted=lnex.extract(text)


o=[]
for e in extracted:
  entity={
    "entity": {
      "mention": e[0],
      "offset": e[1],
      "match": e[2],
      "locations": e[3]
     }
  }
  o.append(entity)

print(json.dumps(o))