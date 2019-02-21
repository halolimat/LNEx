import json, re
from shapely.geometry import MultiPoint
import sys 
sys.path.append("LNEx")
import LNEx as lnex
import redis
from DRDB import DRDB

from subprocess import Popen, PIPE
import os
from JobQueue import JobQueue
jq=JobQueue("jobqueue",host='LNEx-redis')

def logit(text):
  with open("/var/log/LNEx.log", "a") as fp:
    fp.write(str(text))
    fp.write("\n")


logit("INIT LOADER INIT")

db=DRDB("/var/local/LNEx.db")
args=sys.argv

name=args[1]
zoneInfo=db.get_zone(name)
if zoneInfo:
  bb=zoneInfo[0][2]
  bb = [ float(n) for n in bb[1:-1].split(",") ]
  print(bb)
text=args[2]

def HKRset(key,val,db):
  r=redis.Redis(host='LNEx-redis')
  _pre="LNEx_"
  _key=str(_pre)+str(key)
  r.set(_key, val)
  db.addRedisKey(_key)

def init_using_elasticindex(bb, cache, augmentType, dataset, capital_word_shape):
    lnex.elasticindex(conn_string='130.108.86.153:9201', index_name="photon")

    lnex.initialize( bb, augmentType=augmentType,
                                    cache=cache,
                                    dataset_name=dataset,
                                    capital_word_shape=capital_word_shape,
                                    isInit=True)

bbs = {}
bbs[name] = bb
dataset = name

import math
R=6371
PI=3.14159265
X1=math.fabs(math.cos(math.radians(bbs[dataset][2]))-math.cos(math.radians(bbs[dataset][0])))
X2=math.fabs(bbs[dataset][3]-bbs[dataset][1])
A=(PI/180.0)*math.pow(R,2)*X1*X2
size="KM:"+str(A)
logit(size)

init_using_elasticindex(bbs[dataset], cache=False, augmentType="HP", 
                                   dataset=dataset, capital_word_shape=False)

HKRset(str(dataset)+"_ready",1,db)
try:
  db.destroy_connection()
except:
  pass
print("...done")

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