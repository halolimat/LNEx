from DRDB import DRDB
import sys
from subprocess import Popen, PIPE
import redis
import time
import traceback as tb

args=sys.argv

db=DRDB("/var/local/LNEx.db")
STALETIME=1000*60*60*1 #1 HOUR

def help():
  print("create user <name> <email>    ---> key")
  print("list users                    ---> [...]")
  print("list zones                    ---> [...]")
  print("list housecleaning            ---> [...]")
  print("activate user <name> <level>  ---> T/F")
  print("deactivate user <name>        ---> T/F")
  print("deactivate zone <name>        ---> T/F")
  print("query <name> <text>           ---> [...]")
  print("HC minor                      ---> T/F")
  print("reset system                  ---> T/F")
  print("reset active                  ---> T/F")

try:
  # create
  if args[1] == "create":
    if args[2] == "user":
      key=db.create_user(str(args[3]), str(args[4]))
      print("user key:", key)
    else:
      print("unknown command: " + str(args[1]) + str(args[2]))
  # list
  elif args[1] == "list":
    if args[2] == "users":
      r=db.list_users()
      for i in r:
        print(i)
    elif args[2] == "zones":
      r=db.list_zones()
      for i in r:
        print(i)
    elif args[2] == "housecleaning":
      r=db.list_housecleaning()
      for i in r:
        print(i)
    else:
      print("unknown command: " + str(args[1]) + str(args[2]))
  # activate
  elif args[1] == "activate":
    if args[2] == "user":
      try:
        try:
          level=args[4]
          if level != "2" and level != "3" and level != "4" and level != "5":
            level = 1
        except:
          level=1
        r=db.activate_user(args[3], level)
        print(r)
      except:
        print("user not found")
  # deactivate
  elif args[1] == "deactivate":
    if args[2] == "user":
      try:
        r=db.suspend_user((args[3]))
      except:
        print("user not found")
    elif args[2] == "zone":
      try:
        r=db.suspend_zone((args[3]))
      except:
        print("zone not found")
  # query
  elif args[1] == "query":
    cmd = [
      '/root/workspace/LNEx/LNExEnv',
      '/root/workspace/LNEx/LNExLocal']+args[2:]
    proc = Popen(
      cmd,
      stdout=PIPE,
      stderr=PIPE)
    o=proc.stdout.read().decode('utf-8')
    print(o)
    #e=proc.stderr.read()
    #print(e)
  elif args[1] == "clean":
    try:
      r=db.list_zones()
      for zone in r:
        if int(round(time.time() * 1000)) - int(zone[3]) > STALETIME:
          db.suspend_zone(zone[1])
    except:
      with open("/var/log/LNEx.log", "a") as fp:
        var = tb.format_exc()
        fp.write(str(var))
  elif args[1] == "HC":
    if args[2] == "minor":
      r=db.clearMinorKeys()
      print(r)
  elif args[1] == "help":
    help()
  elif args[1] == "reset":
    if args[2] == "system":
      r = redis.Redis(host='LNEx-redis')
      r.flushdb()
      r.set("LNEx_ZONEINIT_ACTIVE", 0)
      db.clear_zone_table()
      db.clear_user_table()
      db.clear_housekeeping_table()
    if args[2] == "active":
      r = redis.Redis(host='LNEx-redis')
      r.set("LNEx_ZONEINIT_ACTIVE", 0)
  else:
    print("unknown command: " + str(args[1]))
    print(help())
except:
  print("missing arguments")
db.destroy_connection()