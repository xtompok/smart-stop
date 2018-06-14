#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Show departs from given stop with delay and wheelchair accessibility information
# Quick hack on https://github.com/xtompok/departs


import sys
import psycopg2
import datetime


window = 30 # window in minutes

def getLineTrips(stops,services):
	cur.execute("SELECT route_id FROM gtfs_routes WHERE route_short_name ='"+sys.argv[2]+"';")
	route = cur.fetchall()[0][0]

	strservices = ",".join(services)
	cur.execute("SELECT DISTINCT trip_id FROM gtfs_trips WHERE route_id = '"+route+"' AND (service_id IN ("+strservices+"));")
	trips = list(map(lambda x: {"route":sys.argv[2], "trip":x[0]}, cur.fetchall()))
	return trips

def getTrips(stops,services):
	strservices = ",".join(services)
	cur.execute("SELECT DISTINCT r.route_short_name,t.trip_id,t.wheelchair_accessible FROM gtfs_trips AS t INNER JOIN gtfs_routes AS r ON t.route_id = r.route_id WHERE t.service_id IN ("+strservices+") ;")
	trips = list(map(lambda x: {"route":x[0],"trip":x[1],"wheelchair":x[2]}, cur.fetchall()))
	return trips

try:
	conn = psycopg2.connect("dbname='gtfs_pid'")
except:
	print ("I am unable to connect to the database")

cur = conn.cursor()

name = sys.argv[1]
name = "% ".join(name.split(" "))+"%"
cur.execute(" SELECT stop_id FROM gtfs_stops WHERE stop_name LIKE '"+name+"';")
stops = list(map(lambda x: x[0],cur.fetchall()))

now = datetime.datetime.now()
day = now.strftime("%A").lower()
time = now.strftime("%X")
time_last = (now+datetime.timedelta(minutes=window)).strftime("%X")
date = now.strftime("%Y-%m-%d")
cur.execute("SELECT service_id FROM gtfs_calendar WHERE "+day+"=1 AND start_date <= '"+date+"' AND end_date >= '"+date+"';")
services = list(map(lambda x: "'"+x[0]+"'",cur.fetchall()))

if len(sys.argv) == 2:
	trips = getTrips(stops,services)
if len(sys.argv) == 3:
	trips = getLineTrips(stops,services)


cons = []
for trip in trips:
	route = trip["route"]
	wheelchair = trip["wheelchair"]
	trip = trip["trip"]
	cur.execute("SELECT stop_sequence FROM gtfs_stop_times WHERE trip_id = '"+str(trip)+"' AND stop_id IN ('"+"','".join(stops)+"') AND departure_time > '"+time+"' AND departure_time < '"+time_last+"' ORDER BY stop_sequence;")
	try:
		seq = cur.fetchall()[0][0]
	except IndexError:
		continue
	cur.execute("SELECT * FROM gtfs_stop_times WHERE trip_id='"+str(trip)+"' AND stop_sequence >= "+str(seq)+" ORDER BY stop_sequence;")
	stoptimes = cur.fetchall()
	con = []
	for stop in stoptimes:
		cur.execute("SELECT stop_name FROM gtfs_stops WHERE stop_id = '"+stop[3]+"';")
		name = cur.fetchall()[0][0]
		con.append((name,stop[1],stop[2]))
	cons.append({"route":route,"con":con,"wheelchair":wheelchair,"trip":trip})
def concmp(x,y):
	(hx,mx,sx) = x["con"][0][2].split(":")
	(hy,my,sy) = y["con"][0][2].split(":")
	depx = datetime.time(hour = int(hx),minute = int(mx), second = int(sx))
	depy = datetime.time(hour = int(hy),minute = int(my), second = int(sy))
	
	if depx > depy:
		return 1
	if depx == depy:
		return 0
	return -1

def cmp_to_key(mycmp):
	'Convert a cmp= function into a key= function'
	class K(object):
		def __init__(self, obj, *args):
			self.obj = obj
		def __lt__(self, other):
		       return mycmp(self.obj, other.obj) < 0
		def __gt__(self, other):
		       return mycmp(self.obj, other.obj) > 0
		def __eq__(self, other):
		       return mycmp(self.obj, other.obj) == 0
		def __le__(self, other):
		       return mycmp(self.obj, other.obj) <= 0  
		def __ge__(self, other):
			return mycmp(self.obj, other.obj) >= 0
		def __ne__(self, other):
		       return mycmp(self.obj, other.obj) != 0
	return K

cons.sort(key=cmp_to_key(concmp))

for con in cons:
	(dh,dm,ds) = con["con"][0][2].split(":")
	now = datetime.datetime.now()
	depsec = int(dh)*3600+int(dm)*60+int(ds)
	nowsec = now.hour*3600+now.minute*60+now.second
	dsec = depsec-nowsec
	if dsec < 0:
		continue
	if con["wheelchair"]==1:
		wch="♿"
	else:
		wch=" "


	cur.execute("SELECT delay FROM pos_log WHERE trip_id = %s AND to_timestamp(timestamp) > now() - interval '10 mins' ORDER BY timestamp DESC",(con["trip"],));
	res = cur.fetchall()
	if res:
		delay = "({})".format(int(res[0][0]/60))
	else:
		delay = ""
	print("{:<5}{:<4}->{:30} {:5} {}".format(con["route"],wch,con["con"][-1][0],int(dsec/60),delay))
#	print(con["con"][-1][0])
#	for stop in con["con"]:
#		print("{:30}	{}	{}".format(stop[0],stop[1],stop[2]))
#	print("--------------------------"	)

