#!/usr/bin/python3

# Find pairs of stops which are less than 200 m apart
# Very stupid approach, not optimized SQL, takes a lot of time

import psycopg2
import csv


conn = psycopg2.connect("dbname=gtfs_pid user=jethro")
cur = conn.cursor()

cur.execute(" SELECT s1.stop_id, s1.stop_lon, s1.stop_lat, s2.stop_id, s2.stop_lon, s2.stop_lat FROM gtfs_stops AS s1 CROSS JOIN gtfs_stops AS s2 WHERE ST_Distance(ST_Transform(ST_setsrid(ST_Makepoint(s1.stop_lon,s1.stop_lat),4326),5514),ST_transform(st_setsrid(st_makepoint(s2.stop_lon,s2.stop_lat),4326),5514)) < 200;")

nearby_stops = cur.fetchall()

with open("nearby.csv","w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(nearby_stops)
