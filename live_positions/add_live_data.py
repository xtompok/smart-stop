#!/usr/bin/python3


import sys
import json
import psycopg2


data = None

with open(sys.argv[1]) as posfile:
    data = json.load(posfile)

conn = psycopg2.connect("dbname=gtfs_pid user=jethro")
cur = conn.cursor()

for pos in data["tripUpdates"]:
    cur.execute("INSERT INTO pos_log VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(
            pos["tripId"],
            pos["routeId"],
            pos["routeName"],
            pos["cisRouteId"],
            pos["tripNumber"],
            pos["headsign"],
            pos["runningNumber"],
            pos["canceled"],
            pos["trackingStatus"],
            pos["wheelchairAccess"],
            pos["lat"],
            pos["lon"],
            pos["delay"],
            pos["measuredStopId"],
            pos["measuredStopSequence"],
            pos["timestamp"])
        )
conn.commit()
