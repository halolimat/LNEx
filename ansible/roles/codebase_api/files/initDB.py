from DRDB import DRDB
db=DRDB("/var/local/LNEx.db")
db.create_zone_table()
db.create_user_table()
db.create_housekeeping_table()
db.destroy_connection()