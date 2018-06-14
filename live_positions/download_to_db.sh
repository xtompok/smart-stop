#!/bin/sh

while true
do 
	FILENAME=data/`date "+%Y-%m-%d_%H-%M-%S"`.json
	wget "https://pid.jakluk.me/trip_updates.json" -O $FILENAME
	./add_live_data.py $FILENAME
	sleep 10
done
