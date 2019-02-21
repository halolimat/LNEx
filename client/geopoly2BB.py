#from osgeo import ogr
import json;
filename="test.geojson"
with open (filename, "r") as myfile:
    data=myfile.read()

dataset = json.loads(data)


def findMin(c):
    global which1,min1,min2
    for x in c:
        if type(x) == type([]):
            findMin(x)
        else:
            if which1:
                if x < min1:
                    min1 = x
            else:
                if x < min2:
                    min2 = x
            which1 = not which1

def findMax(c):
    global which2,max1,max2
    for x in c:
        if type(x) == type([]):
            findMax(x)
        else:
            if which2:
                if x > max1:
                    max1 = x
            else:
                if x > max2:
                    max2 = x
            which2 = not which2

for f in dataset["features"]:
    c = f["geometry"]["coordinates"]
    min1=999999999999.9
    min2=999999999999.9
    max1=-999999999999.9
    max2=-999999999999.9
    which1=False
    which2=False
    findMin(c)
    findMax(c)
    bbox=[min2,min1,max2,max1]
    name=f['properties']['title']
    print(name,bbox)

exit(0)

with open("yourOutputFile.geojson","w") as f:
    json.dump(dataset,f)