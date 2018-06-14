#!/usr/bin/python3

# Calculate current delay on each segment between stops
# Calculates median delay for each segment between stops, where there have been at least two vehicles passing in last 15 minutes
# Real position info (not interpolated) is required to be sent from the stops by the vehicle.

import psycopg2
import statistics
import csv


conn = psycopg2.connect("dbname=gtfs_pid user=jethro")
cur = conn.cursor()

cur.execute("SELECT trip_id FROM gtfs_trips");
trip_ids = list(map(lambda x:x[0],cur.fetchall()))

sections = {}

for trip_id in trip_ids:
    cur.execute("SELECT stop_id FROM gtfs_stop_times WHERE trip_id = %s ORDER BY stop_sequence",(trip_id,))
    stops = list(map(lambda x:x[0],cur.fetchall()))
    memstop = stops[0]
    for stop in stops:
        sections[(memstop,stop)] = []
        memstop = stop

for (from_id,to_id) in sections:
    #cur.execute("SELECT trip_id,delay FROM pos_log WHERE trackingstatus = 2 AND to_timestamp(timestamp) > (now()- interval '15 minutes') AND measuredstopid = %s ;",(to_id,))
    cur.execute("SELECT trip_id,delay FROM pos_log WHERE trackingstatus = 2 AND to_timestamp(timestamp) > (timestamp '2018-06-08 17:00:00' - interval '15 minutes') AND measuredstopid = %s ;",(to_id,))
    trips = cur.fetchall()
    for (trip,startdelay) in trips:
        cur.execute("SELECT delay FROM pos_log WHERE trackingstatus = 2 AND measuredstopid = %s AND trip_id = %s ;",
                (from_id,trip))
        try:
            enddelay = cur.fetchall()[0][0]
        except:
            continue
        ddelay = enddelay - startdelay
        sections[(from_id,to_id)].append(ddelay)

with open("delays.csv","w") as delfile:
    writer = csv.writer(delfile)
    for ((from_id,to_id),ddelays) in sections.items():
        if len(ddelays)>=2:
            median = statistics.median(ddelays)
            writer.writerow((from_id,to_id,median))

        
   
