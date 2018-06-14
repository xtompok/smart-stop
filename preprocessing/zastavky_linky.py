#!/usr/bin/python3

# For each trip find important stops
# Important stop is the stop, where are at least four other lines more than on the previous stop

import psycopg2

conn = psycopg2.connect("dbname=gtfs_pid user=jethro")
cur = conn.cursor()

cur.execute("SELECT s.stop_name,array_agg(DISTINCT r.route_short_name) FROM gtfs_stops AS s INNER JOIN gtfs_stop_times AS st ON st.stop_id = s.stop_id INNER JOIN gtfs_trips AS t ON st.trip_id = t.trip_id INNER JOIN gtfs_routes AS r ON r.route_id = t.route_id WHERE r.route_short_name NOT LIKE '9_' AND r.route_short_name NOT LIKE '9__' GROUP BY s.stop_name;")

res = cur.fetchall()
stop_lines = {r[0]:set(r[1]) for r in res}


cur.execute("SELECT trip_id FROM gtfs_trips;")
trip_ids = list(map(lambda x: x[0],cur.fetchall()))
for trip_id in trip_ids:
    cur.execute("SELECT s.stop_name,s.stop_id,st.stop_sequence FROM gtfs_stops AS s INNER JOIN  gtfs_stop_times AS st ON s.stop_id = st.stop_id WHERE trip_id=%s ORDER BY st.stop_sequence",(trip_id,))
    stops = cur.fetchall()
    try:
        memlines = stop_lines[stops[0][0]]
    except:
        memlines = set()
    newlines = [set()]
    ss = [stops[0][2]]
    for stop in stops[1:]:
        (name,aid,ssid) = stop
        ss.append(ssid)
        try:
            lines = stop_lines[name]
        except KeyError:
            newlines.append(set())
            continue
        dlines = lines-memlines
        if len(dlines) >= 4:
            newlines.append(aid)
        else:
            newlines.append(set())
        memlines = lines
#        print(stop,dlines)
    if not newlines[-1]:
        newlines[-1] = stops[-1][1]
    for i in range(len(newlines)-2,-1,-1):
        if not newlines[i]:
            newlines[i] = newlines[i+1]
    
    for i in range(len(newlines)):
        cur.execute("INSERT INTO important_stops VALUES (%s,%s,%s)",(trip_id,ss[i],newlines[i]))
#    print(newlines)
conn.commit()

    
