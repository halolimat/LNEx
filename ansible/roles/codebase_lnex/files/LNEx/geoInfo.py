import json, re
import sys 
import redis
from DRDB import DRDB
import dill
r = redis.Redis(host='LNEx-redis')

from subprocess import Popen, PIPE
import os
from JobQueue import JobQueue
jq=JobQueue("jobqueue",host='LNEx-redis')

db=DRDB("/var/local/LNEx.db")
args=sys.argv

dataset_name=args[1]
geoIDs=args[2]
geoIDs=geoIDs.split(",")
resultKey=args[3]

def HKRset(key,val,db):
  r=redis.Redis(host='LNEx-redis')
  _pre="LNEx_"
  _key=str(_pre)+str(key)
  r.set(_key, val)
  db.addRedisKey(_key)

zoneInfo=db.get_zone(dataset_name)
if zoneInfo:
  geo_info_raw=r.get("LNEx_"+str(dataset_name)+"_geo_info")
  geo_info = dill.loads(geo_info_raw)
else:
  print("Error")

mainO={}

for location_id in geoIDs:

  try:
    point=geo_info[str(location_id)]['geo_item']['point']
  except:
    point=None
  try:
    extent=geo_info[str(location_id)]['geo_item']['extent']
  except:
    extent=None
  try:
    osm_id=geo_info[str(location_id)]['geo_item']['osm_id']
  except:
    osm_id=None

  o={
    'point': point,
    'extent': extent,
    'osm_id': osm_id
  }

  mainO[location_id]=o

#f_o=json.dumps(mainO)
HKRset(str(resultKey)+"_results",json.dumps(mainO),db)
HKRset(str(resultKey)+"_resultReady",1,db)
#with open("tmp.tmp", "w") as fp:
#  fp.write(f_o)
#print(f_o)


try:
  db.destroy_connection()
except:
  pass

r=redis.Redis(host='LNEx-redis')
r.set("LNEx_ZONEINIT_ACTIVE", 0)

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