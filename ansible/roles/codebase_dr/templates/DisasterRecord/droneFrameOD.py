import object_detection
from object_detection.ObjectDetector import ObjectDetector
OD = ObjectDetector()

URL="http://130.108.86.152/droneFrames/{}/frame{}.jpg"

with open("testout.o", "w") as fp:
  fp.write("")

def doExtract(frameSet, frame):

  obj = OD.extract(URL.format(frameSet,frame))
  with open("testout.o", "a") as fp:
    fp.write(str(obj))
    fp.write("\n")

doExtract("example03","0")
doExtract("example03","150")
doExtract("example03","300")
doExtract("example03","450")
doExtract("example03","600")
doExtract("example03","750")
doExtract("example03","900")
doExtract("example03","1050")
doExtract("example03","1200")
doExtract("example03","1350")
doExtract("example03","1500")
doExtract("example03","1650")
doExtract("example03","1800")
doExtract("example03","1950")
#doExtract("example03","900")
