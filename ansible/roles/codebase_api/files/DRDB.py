import sqlite3
from sqlite3 import Error
import sys
import time
import traceback as tb
import redis
import random

class DRDB:

  def __init__(self, db_file):
    self.db_file = db_file
    self._create_connection()
    #zones allowed,extractions/min,results/min,geoinfo/min
    self.apiLevel = {
      1: [25,120,120,120],
      2: [50,120,120,120],
      3: [75,240,240,240],
      4: [150,240,240,240],
      5: [9999,9999,9999,9999]
    }

  def genRandKey(self):
    millis = int(round(time.time() * 1000))
    color = "%07x" % random.randint(0, 0xFFFFFFF)
    p1='{:x}'.format(millis)
    o=p1+str(color)
    return str(o)

  def _create_connection(self):
    try:
      self.conn = sqlite3.connect(self.db_file)
      #print(sqlite3.version)
    except Error as e:
      print(e)

  def destroy_connection(self):
    self.conn.close()

  def _exeCreate(self, cmd):
    if not self.conn:
      print("Not Connected")
      sys.exit(1)
    c=self.conn.cursor()
    c.execute(cmd)
    self.conn.commit()

  def _exeQuery(self, cmd):
    if not self.conn:
      print("Not Connected")
      sys.exit(1)
    c=self.conn.cursor()
    c.execute(cmd)
    f=c.fetchall()
    return f

  def create_zone_table(self):
    r = redis.Redis(host='DR-redis')
    r.set("LNEx_ZONEINIT_ACTIVE", 0)
    cmd="CREATE TABLE IF NOT EXISTS zone (\
          id integer PRIMARY KEY,\
          name text NOT NULL,\
          bb text NOT NULL,\
          last_active text DEFAULT ('-1'),\
          cache_ts text DEFAULT ('-1'),\
          inMem integer DEFAULT (0),\
          ownerKey text NOT NULL,\
          CONSTRAINT unique_names UNIQUE (name)\
        );"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def clear_zone_table(self):
    cmd="DELETE FROM zone;"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def create_user_table(self):
    cmd="CREATE TABLE IF NOT EXISTS user (\
          id integer PRIMARY KEY,\
          name text NOT NULL,\
          email text NOT NULL,\
          key text,\
          last_used text DEFAULT ('-1'),\
          active integer DEFAULT (0),\
          zn_cnt integer DEFAULT (0),\
          ex_cnt integer DEFAULT (0),\
          rs_cnt integer DEFAULT (0),\
          go_cnt integer DEFAULT (0),\
          CONSTRAINT unique_names UNIQUE (name)\
        );"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def clear_user_table(self):
    cmd="DELETE FROM user;"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def create_housekeeping_table(self):
    cmd="CREATE TABLE IF NOT EXISTS housekeeping (\
          id integer PRIMARY KEY,\
          redisKey text NOT NULL,\
          regDate integer DEFAULT (0),\
          CONSTRAINT unique_keys UNIQUE (redisKey)\
        );"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def clear_housekeeping_table(self):
    cmd="DELETE FROM housekeeping;"
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def addRedisKey(self,key):
    millis = int(round(time.time() * 1000))
    cmd="SELECT * FROM housekeeping WHERE redisKey = '{}';".format(str(key))
    r=self._exeQuery(cmd)
    if len(r) > 0:
      cmd="UPDATE housekeeping SET regDate = {};".format(int(millis))
      try:
        self._exeCreate(cmd)
        return True
      except:
        return False
    else:
      cmd="INSERT INTO housekeeping\
            (redisKey, regDate)\
           VALUES\
           ('{}','{}');".format(
              str(key),
              int(millis))
      try:
        self._exeCreate(cmd)
        return True
      except:
        return False

  def delKey(self, key):
    r = redis.Redis(host='DR-redis')
    r.delete(key)


  def clearMinorKeys(self):
    millis = int(round(time.time() * 1000))
    cmd="SELECT * FROM housekeeping;"
    r=self._exeQuery(cmd)
    matched=False
    for can in r:
      if "_resultReady" in can[1]:
        if millis - int(can[2]) >= 1000*60*30:
          self.delKey(can[1])
          cmd="DELETE FROM housekeeping where redisKey = '{}';".format(str(can[1]))
          self._exeCreate(cmd)
          matched=True
      if "_queryText" in can[1]:
        if millis - int(can[2]) >= 1000*60*30:
          self.delKey(can[1])
          cmd="DELETE FROM housekeeping where redisKey = '{}';".format(str(can[1]))
          self._exeCreate(cmd)
          matched=True
      if "_results" in can[1]:
        if millis - int(can[2]) >= 1000*60*30:
          self.delKey(can[1])
          cmd="DELETE FROM housekeeping where redisKey = '{}';".format(str(can[1]))
          self._exeCreate(cmd)
          matched=True
    return matched


  def create_user(self, name, email):
    #token="THISNEEDSREPLACED"
    key=self.genRandKey()
    cmd="INSERT INTO user\
           (name,email,key)\
         VALUES\
         ('{}','{}','{}');".format(
            str(name),
            str(email),
            str(key))
    try:
      self._exeCreate(cmd)
      return key
    except:
      return False

  def list_housecleaning(self):
    cmd="SELECT * FROM housekeeping;"
    r=self._exeQuery(cmd)
    return r

  def activate_user(self, name, level):
    cmd="UPDATE user SET \
           active = {}\
         WHERE\
         name = '{}';".format(int(level),
            str(name))
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def suspend_user(self, name):
    cmd="UPDATE user SET \
           active = 0\
         WHERE\
         name = '{}';".format(
            str(name))
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def confirm_owner(self, zone, key):
    cmd="SELECT * from zone WHERE name = '{}' AND ownerKey = '{}';".format(str(zone),str(key))
    try:
      r=self._exeQuery(cmd)
      if len(r) > 0:
        return True
      else:
        return False
    except:
      return False

  def suspend_zone(self, zone):
    o = True
    r = redis.Redis(host='DR-redis')
    try:
      r.delete("LNEx_"+str(name)+"_ready")
      r.delete("LNEx_"+str(name)+"_new_geo_locations")
      r.delete("LNEx_"+str(name)+"_geo_info")
      r.delete("LNEx_"+str(name)+"_extended_words3")
      r.memory_purge()
    except:
      o=False
    cmd="DELETE FROM zone WHERE\
         name = '{}';".format(
            str(zone))
    try:
      self._exeCreate(cmd)
      return o
    except:
      return False

  def create_zone(self, name, bb, key):
    cmd="INSERT INTO zone\
           (name,bb,ownerKey)\
         VALUES\
         ('{}','{}','{}');".format(
            str(name),
            str(bb),
            str(key))
    try:
      self._exeCreate(cmd)
      return True
    except:
      return False

  def list_users(self):
    cmd="SELECT * FROM user;"
    r=self._exeQuery(cmd)
    return r

  def list_zones(self):
    cmd="SELECT * FROM zone;"
    r=self._exeQuery(cmd)
    return r

  def verify_user(self,name,key):
    cmd="SELECT name FROM user WHERE name='{}' AND key='{}' AND active > 0;".format(str(name),str(key))
    r=self._exeQuery(cmd)
    if len(r) > 0:
      return True
    else:
      return False

  def verify_key(self,key):
    cmd="SELECT key FROM user WHERE key='{}' AND active > 0;".format(str(key))
    r=self._exeQuery(cmd)
    if len(r) > 0:
      return True
    else:
      return False

  def log_user(self, key):
    millis = int(round(time.time() * 1000))
    cmd="UPDATE user SET\
           last_used = '{}'\
         WHERE\
         key = '{}';".format(
          int(millis), str(key))
    try:
      r=self._exeQuery(cmd)
      return True
    except:
      return False

  def log_zone(self, zone):
    millis = int(round(time.time() * 1000))
    cmd="UPDATE zone SET\
           last_used = '{}'\
         WHERE\
         name = '{}';".format(
          int(millis), str(zone))
    try:
      r=self._exeQuery(cmd)
      return True
    except:
      return False

  def reduce_zoneCnt(self, key):
    try:
      cmd="UPDATE user SET zn_cnt = zn_cnt - 1 WHERE key='{}'".format(str(key))
      r=self._exeCreate(cmd)
      return True
    except:
      return False

  def zn_count(self, key):

    cmd="SELECT zn_cnt FROM user WHERE key='{}'".format(str(key))
    try:
      r=self._exeQuery(cmd)
      cur_count = int(r[0][0])
      print(cur_count)
      if cur_count == 0:
        self.log_user(str(key))
        cmd="UPDATE user SET zn_cnt = zn_cnt + 1 WHERE key='{}'".format(str(key))
        r=self._exeCreate(cmd)
        return True
      else:
        cmd="SELECT active FROM user WHERE key='{}'".format(str(key))
        r=self._exeQuery(cmd)
        cur_level = int(r[0][0])
        if cur_count < self.apiLevel[cur_level][0]:
          cmd="UPDATE user SET zn_cnt = zn_cnt + 1 WHERE key='{}'".format(str(key))
          r=self._exeCreate(cmd)
          return True
        else:
          #cmd="SELECT last_used FROM user WHERE key='{}'".format(str(key))
          #r=self._exeQuery(cmd)
          #last_used = int(r[0][0])
          #if int(round(time.time() * 1000)) - last_used >= 1000*60*60*24:
          #  cmd="UPDATE user SET zn_cnt = 0 WHERE key='{}'".format(str(key))
          #  r=self._exeCreate(cmd)
          #  return True
          #else:
          #  return False
          return False
    except:
      var = tb.format_exc()
      with open("/var/log/LNEx.log", "a") as fp:
        fp.write("::DRDB ERROR::")
        fp.write(str(var))
      return False


  def ex_count(self, key):

    cmd="SELECT ex_cnt FROM user WHERE key='{}'".format(str(key))
    try:
      r=self._exeQuery(cmd)
      cur_count = int(r[0][0])
      print(cur_count)
      if cur_count == 0:
        self.log_user(str(key))
        cmd="UPDATE user SET ex_cnt = ex_cnt + 1 WHERE key='{}'".format(str(key))
        r=self._exeCreate(cmd)
        return True
      else:
        cmd="SELECT active FROM user WHERE key='{}'".format(str(key))
        r=self._exeQuery(cmd)
        cur_level = int(r[0][0])
        if cur_count < self.apiLevel[cur_level][1]:
          cmd="UPDATE user SET ex_cnt = ex_cnt + 1 WHERE key='{}'".format(str(key))
          r=self._exeCreate(cmd)
          return True
        else:
          cmd="SELECT last_used FROM user WHERE key='{}'".format(str(key))
          r=self._exeQuery(cmd)
          last_used = int(r[0][0])
          if int(round(time.time() * 1000)) - last_used >= 1000*60*60:
            cmd="UPDATE user SET ex_cnt = 0 WHERE key='{}'".format(str(key))
            r=self._exeCreate(cmd)
            return True
          else:
            return False
    except:
      var = tb.format_exc()
      with open("/var/log/LNEx.log", "a") as fp:
        fp.write("::DRDB ERROR::")
        fp.write(str(var))
      return False

  def rs_count(self, key):

    cmd="SELECT rs_cnt FROM user WHERE key='{}'".format(str(key))
    try:
      r=self._exeQuery(cmd)
      cur_count = int(r[0][0])
      print(cur_count)
      if cur_count == 0:
        self.log_user(str(key))
        cmd="UPDATE user SET rs_cnt = rs_cnt + 1 WHERE key='{}'".format(str(key))
        r=self._exeCreate(cmd)
        return True
      else:
        cmd="SELECT active FROM user WHERE key='{}'".format(str(key))
        r=self._exeQuery(cmd)
        cur_level = int(r[0][0])
        if cur_count < self.apiLevel[cur_level][2]:
          cmd="UPDATE user SET rs_cnt = rs_cnt + 1 WHERE key='{}'".format(str(key))
          r=self._exeCreate(cmd)
          return True
        else:
          cmd="SELECT last_used FROM user WHERE key='{}'".format(str(key))
          r=self._exeQuery(cmd)
          last_used = int(r[0][0])
          if int(round(time.time() * 1000)) - last_used >= 1000*60:
            cmd="UPDATE user SET rs_cnt = 0 WHERE key='{}'".format(str(key))
            r=self._exeCreate(cmd)
            return True
          else:
            return False
    except:
      var = tb.format_exc()
      with open("/var/log/LNEx.log", "a") as fp:
        fp.write("::DRDB ERROR::")
        fp.write(str(var))
      return False

  def go_count(self, key):

    cmd="SELECT go_cnt FROM user WHERE key='{}'".format(str(key))
    try:
      r=self._exeQuery(cmd)
      cur_count = int(r[0][0])
      print(cur_count)
      if cur_count == 0:
        self.log_user(str(key))
        cmd="UPDATE user SET go_cnt = go_cnt + 1 WHERE key='{}'".format(str(key))
        r=self._exeCreate(cmd)
        return True
      else:
        cmd="SELECT active FROM user WHERE key='{}'".format(str(key))
        r=self._exeQuery(cmd)
        cur_level = int(r[0][0])
        if cur_count < self.apiLevel[cur_level][3]:
          cmd="UPDATE user SET go_cnt = go_cnt + 1 WHERE key='{}'".format(str(key))
          r=self._exeCreate(cmd)
          return True
        else:
          cmd="SELECT last_used FROM user WHERE key='{}'".format(str(key))
          r=self._exeQuery(cmd)
          last_used = int(r[0][0])
          if int(round(time.time() * 1000)) - last_used >= 1000*60:
            cmd="UPDATE user SET go_cnt = 0 WHERE key='{}'".format(str(key))
            r=self._exeCreate(cmd)
            return True
          else:
            return False
    except:
      var = tb.format_exc()
      with open("/var/log/LNEx.log", "a") as fp:
        fp.write("::DRDB ERROR::")
        fp.write(str(var))
      return False


  def check_name(self, name):
    cmd="SELECT name FROM zone WHERE name='{}';".format(str(name))
    r=self._exeQuery(cmd)
    if len(r) > 0:
      return False
    else:
      return True

  def get_zone(self, name):
    cmd="SELECT * FROM zone WHERE name='{}';".format(str(name))
    r=self._exeQuery(cmd)
    if len(r) > 0:
      return r
    else:
      return False

# EXAMPLE USEAGE:
# from dbtest import DRDB
# db=DRDB("test.db")
# db.create_campaign_table()
# db.create_user_table()
# db.create_user("mike","mike.partin@gmail.com")
# db.create_campaign("dayton","[125,44,45,12]")
# db.list_users()
# db.list_campaigns()
# db.verify_token("WILLFAIL")
# db.verify_token("THISNEEDSREPLACED")
# db.destroy_connection()