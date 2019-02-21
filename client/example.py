from LNExAPI import LNExAPI

# how to parse the data returned
def displayResults(results):
  for result in results:
    print("Matches for:",result['text'])
    for entity in result['entities']:
      print("[ ]-->",entity['match'])
      for location in entity['locations']:
        print("   [ ]-->",str(location['coordinate']['lat'])+","+str(location['coordinate']['lon']))

#give your key to init
lnex = LNExAPI(key="168e8944cc2d86d7f7",host="http://130.108.86.152/")

#init a zone
lnex.initZone([-84.6447033333,39.1912856591,-83.2384533333,40.0880515857],"dayton")
#lnex.initZone([-74.5372,40.3961,-73.3397,41.0787],"newyork")
#lnex.initZone([-81.4696,34.9303,-80.2721,35.6655],"charlotte")
#lnex.initZone([-79.536,33.3436,-78.3385,34.0929],"myrtle beach")
#lnex.initZone([-90.58,34.77,-89.38,35.5],"memphis")
#lnex.initZone([-10.57,36.18,38.92,59.13],"europe") #will not init because of LNEx size restriction

#lnex.zoneReady("dayton")

#lnex.pollZoneReady("dayton")



text=[
    "Have you seen the kettering towers?",
    "You should check out 3rd street",
    "meet me over at wright state university",
    "head over to the Mudlick Tap House on 2nd street, it's close to Miami River",
    "I'm heading to Table 33, they got good food in dayton",
    "Have you tried Spend Grain Grill? It's better than Olive Garden",
    "I can meet you at Watervliet Ave.",
    "I've never been to the Dayton Mall",
    "Anybody know where the Sears building is?",
    "I'm looking to get to the library",
    "Wright State University is a great school",
    "Brown Street is where good food is, next to the UD campus",
    "Wright Brothers parkway is also known as Woodman Drive",
    "I live right next to the Dayton Library",
    "The Wingate hotel is just outside my window",
    "I'm looking for China One"]

result_token,results=lnex.pollFullBulkExtract("dayton",text)

displayResults(results)



#o2=lnex.pollBulkExtract("newyork",text)
#o3=lnex.pollBulkExtract("charlotte",text)
#o4=lnex.pollBulkExtract("myrtle beach",text)
#o5=lnex.pollBulkExtract("memphis",text)
