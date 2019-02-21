import subprocess
import time
import redis

r=redis.Redis(host='LNEx-redis')

def isRunning(what):

  proc1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
  proc2 = subprocess.Popen(['grep', '-v', 'grep'], stdin=proc1.stdout,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  proc3 = subprocess.Popen(['grep', what], stdin=proc2.stdout,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
  out, err = proc3.communicate()
  if len(out) == 0:
    return False
  else:
    return True


isClear=0

while True:

  c1=isRunning('initLoader')
  c2=isRunning('geoInfo')
  c3=isRunning('queryBulk')

  if c1 or c2 or c3:
    isClear = 0
  else:
    if isClear<10:
      isClear +=1
    elif isClear == 10:
      r.set("LNEx_ZONEINIT_ACTIVE", 0)
      isClear=0

  time.sleep(2)
