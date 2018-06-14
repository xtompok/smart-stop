#!/bin/sh

cd $(dirname $0)/jrcache
#NAME=`date +"jr_%Y-%m-%d_%H-%M.zip"`
#wget -O $NAME http://opendata.iprpraha.cz/DPP/JR/jrdata.zip
#unzip -o $NAME


FILES="agency calendar calendar_dates routes shapes stops trips stop_times"

for f in $FILES
do
	echo "$f..."
	psql gtfs_pid -c "TRUNCATE TABLE gtfs_$f;"
	cat $f.txt | iconv -f utf-8 -t utf-8 -c |  psql gtfs_pid -c "COPY gtfs_$f FROM STDIN WITH CSV DELIMITER ',' HEADER;"
	psql gtfs_pid -c "ANALYZE gtfs_$f;"
done
cd ..
psql gtfs_pid < GTFS_shapes.sql

