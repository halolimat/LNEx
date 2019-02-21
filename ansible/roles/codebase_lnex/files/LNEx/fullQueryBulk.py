import json, re
from shapely.geometry import MultiPoint
import sys 
sys.path.append("LNEx")
import LNEx as lnex
import redis
from DRDB import DRDB
r = redis.Redis(host='LNEx-redis')
print("query init")

from subprocess import Popen, PIPE
import os
from JobQueue import JobQueue
jq=JobQueue("jobqueue",host='LNEx-redis')

import traceback as tb

def logit(text):
  with open("/var/log/LNEx.log", "a") as fp:
    fp.write(str(text))
    fp.write("\n")

db=DRDB("/var/local/LNEx.db")
args=sys.argv

#user=args[1]
name=args[1]
meta=args[2]
resultKey=args[3]

zoneInfo=db.get_zone(name)
if zoneInfo:
  bb=zoneInfo[0][2]
  bb = [ float(n) for n in bb[1:-1].split(",") ]
  print(bb)
text=r.get("LNEx_"+str(resultKey)+"_queryText").decode('utf-8')
requests=json.loads(text)
#print(user,name,text)

def HKRset(key,val,db):
  r=redis.Redis(host='LNEx-redis')
  _pre="LNEx_"
  _key=str(_pre)+str(key)
  r.set(_key, val)
  db.addRedisKey(_key)

print("QUERY BULK STARTING!")

logit(name)
logit(text)


def init_using_elasticindex(bb, cache, augmentType, dataset, capital_word_shape):
    lnex.elasticindex(conn_string='130.108.86.153:9201', index_name="photon")

    geo_info = lnex.initialize( bb, augmentType=augmentType,
                                    cache=cache,
                                    dataset_name=dataset,
                                    capital_word_shape=capital_word_shape)
    return geo_info

if "data" not in requests:
  o={"results":"\"data\" key not found"}
  #r.set("LNEx"+str(resultKey)+"_results", json.dumps(o))
  HKRset(str(resultKey)+"_results",json.dumps(o),db)
  logit("results not found")

else:
  try:
    logit("stage1")
    bbs = {}
    bbs[name] = bb
    dataset = name

    import math
    R=6371
    PI=3.14159265
    X1=math.fabs(math.cos(math.radians(bbs[dataset][2]))-math.cos(math.radians(bbs[dataset][0])))
    X2=math.fabs(bbs[dataset][3]-bbs[dataset][1])
    A=(PI/180.0)*math.pow(R,2)*X1*X2
    print("KM:",A)

    geo_info = init_using_elasticindex(bbs[dataset], cache=False, augmentType="HP", 
                                       dataset=dataset, capital_word_shape=False)
    logit("stage2")
    f_o=[]
    for d in requests['data']:
      extracted=lnex.extract(str(d))

      o=[]
      for e in extracted:
        if meta == "True":
          entity={
            "entity": {
              "mention": e[0],
              "offset": e[1],
              "match": e[2],
              "locations": e[3]
             }
          }
        else:


          geoIDs=e[3]['main']
          info=[]
          for location_id in geoIDs:

            try:
              osm_id=geo_info[str(location_id)]['geo_item']['osm_id']
            except:
              osm_id=None

            if osm_id:
              import requests
              
              #ESURL="{{ photonip }}"
              ESURL="130.108.86.153"
              #ESPORT = "{{ photonport }}"
              ESPORT="9201"

              res = requests.get("http://{}:{}/photon/_search?q=osm_id:{}".format(ESURL,ESPORT,osm_id))
              rjson = res.json()
              try:
                msg=rjson['hits']['hits'][0]['_source']
                #msg['code']=0
              except:
                msg={'error':'error while trying to query photon db'}

              #info[osm_id]=msg
              info.append(msg)

          entity={
            "mention": e[0],
            "offset": e[1],
            "match": e[2],
            "locations": info
          }
        o.append(entity)
      doc2add={'entities':o,'text':d}
      f_o.append(doc2add)

    logit("stage3")

    HKRset(str(resultKey)+"_results",json.dumps(f_o),db)
    HKRset(str(resultKey)+"_resultReady",1,db)
    print("...done")

    r=redis.Redis(host='LNEx-redis')
    r.set("LNEx_ZONEINIT_ACTIVE", 0)
  except:
    var = tb.format_exc()
    logit(str(var))

if not jq.empty():

  nextJob=jq.get().decode("utf-8").split("<|>")

  if nextJob[0] == "init":
    r.set("LNEx_ZONEINIT_ACTIVE", 1)
    logfile = open('/var/log/LNEx.log', 'a')
    cmd = [
    '/root/workspace/LNEx/LNExEnv',
    'python',
    '/root/workspace/LNEx/initLoader.py',
    str(nextJob[1]),
    "\"void\""]
    devnull = open(os.devnull, 'w')
    proc = Popen(
        cmd,
        shell=False,
        stdin=devnull,
        stdout=logfile,
        stderr=logfile,
        close_fds=True)

  if nextJob[0] == "ext":
    r.set("LNEx_ZONEINIT_ACTIVE", 1)
    logfile = open('/var/log/LNEx.log', 'a')
    cmd = [
    '/root/workspace/LNEx/LNExEnv',
    'python',
    '/root/workspace/LNEx/queryBulk.py',
    str(nextJob[1]),
    str(nextJob[2]),
    str(nextJob[3]),
    ]
    devnull = open(os.devnull, 'w')
    proc = Popen(
        cmd,
        shell=False,
        stdin=devnull,
        stdout=logfile,
        stderr=logfile,
        close_fds=True)
  if nextJob[0] == "extF":
    r.set("LNEx_ZONEINIT_ACTIVE", 1)
    logfile = open('/var/log/LNEx.log', 'a')
    cmd = [
    '/root/workspace/LNEx/LNExEnv',
    'python',
    '/root/workspace/LNEx/fullQueryBulk.py',
    str(nextJob[1]),
    str(nextJob[2]),
    str(nextJob[3]),
    ]
    devnull = open(os.devnull, 'w')
    proc = Popen(
        cmd,
        shell=False,
        stdin=devnull,
        stdout=logfile,
        stderr=logfile,
        close_fds=True)
  if nextJob[0] == "geo":
    r.set("LNEx_ZONEINIT_ACTIVE", 1)
    cmd = [
    '/root/workspace/LNEx/LNExEnv',
    'python',
    '/root/workspace/LNEx/geoInfo.py',
    str(nextJob[1]),
    str(nextJob[2]),
    str(nextJob[3]),
    ]
    devnull = open(os.devnull, 'w')
    proc = Popen(
        cmd,
        shell=False,
        stdin=devnull,
        stdout=logfile,
        stderr=logfile,
        close_fds=True)