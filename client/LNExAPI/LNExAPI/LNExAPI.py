import requests
import time
import json

class LNExAPI:

  def __init__(self,key,host):
    self.key=key
    self.host=host+"apiv1/LNEx/"

  def initZone(self,bb,name):
    uri="initZone?key={}&bb=[{},{},{},{}]&zone={}".format(
      str(self.key),
      bb[0],bb[1],bb[2],bb[3],
      str(name))
    r = requests.get(self.host+uri)
    return r.json()

  def zoneReady(self,name):
    uri="zoneReady?key={}&zone={}".format(
      str(self.key),
      str(name))
    r = requests.get(self.host+uri)
    try:
      rjson = r.json()
      if rjson['code']==0:
        return True
      else:
        return False
    except:
      return False

  def pollZoneReady(self,name,retries=500):
    sleeptime=2
    waiting=True
    a=0
    while waiting:
      if self.zoneReady(name):
        return True
      if a == retries:
        return False
      time.sleep(sleeptime)
      if sleeptime < 32:
        sleeptime=sleeptime*2
      a+=1

  def destroyZone(self,name):
    uri="destroyZone?key={}&zone={}".format(
      str(self.key),
      str(name))
    r = requests.get(self.host+uri)
    return r.json()

  def bulkExtract(self,name,text):
    _text={'data':text}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    uri="bulkExtract?key={}&zone={}".format(
      str(self.key),
      str(name))
    r=requests.post(self.host+uri,data=json.dumps(_text),headers=headers)
    return r.json()

  def fullBulkExtract(self,name,text):
    _text={'data':text}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    uri="fullBulkExtract?key={}&zone={}".format(
      str(self.key),
      str(name))
    r=requests.post(self.host+uri,data=json.dumps(_text),headers=headers)
    return r.json()

  def results(self,token):
    uri="results?key={}&token={}".format(
      str(self.key),
      str(token))
    r=requests.get(self.host+uri)
    return r.json()

  def geoInfo(self,name,locations):
    locations=[int(x) for x in locations]
    uri="geoInfo?&key={}&zone={}&geoIDs={}".format(
      str(self.key),
      str(name),
      str(locations))
    r=requests.get(self.host+uri)
    return r.json()

  def photonInfo(self,osm_id):
    uri="photonID?&key={}&osm_id={}".format(
      str(self.key),
      str(osm_id))
    r=requests.get(self.host+uri)
    return r.json()

  def pollBulkExtract(self,name,text,retries=100):
    sleeptime=2
    r=self.bulkExtract(name,text)
    if 'token' in r:
      token=r['token']
      waiting = True
      a=0
      while waiting:
        if a==retries:
          waiting=False
        results=self.results(token)
        if results['code'] == 7 or results['code'] == 1:
            time.sleep(sleeptime)
            if sleeptime < 32:
              sleeptime=sleeptime*2
        else:
          waiting=False
          if results['code'] == 0:
            results=results['results']
          else:
            results=[]
        a+=1
      return (token,results)
    else:
      return (None,r)

  def pollFullBulkExtract(self,name,text,retries=100):
    sleeptime=2
    r=self.fullBulkExtract(name,text)
    if 'token' in r:
      token=r['token']
      waiting = True
      a=0
      while waiting:
        if a==retries:
          waiting=False
        results=self.results(token)
        if results['code'] == 7 or results['code'] == 1:
            time.sleep(sleeptime)
            if sleeptime < 32:
              sleeptime=sleeptime*2
        else:
          waiting=False
          if results['code'] == 0:
            results=results['results']
          else:
            results=[]
        a+=1
      return (token,results)
    else:
      return (None,r)

  def pollGeoInfo(self,name,locations,retries=100):
    sleeptime=2
    r=self.geoInfo(name,locations)
    if 'token' in r:
      token=r['token']
      waiting = True
      a=0
      while waiting:
        if a==retries:
          waiting=False
        results=self.results(token)
        if results['code'] == 7 or results['code'] == 1:
            time.sleep(sleeptime)
            if sleeptime < 32:
              sleeptime=sleeptime*2
        else:
          waiting=False
          if results['code'] == 0:
            results=results['results']
          else:
            results=[]
        a+=1
      return (token,results)
    else:
      return (None,r)