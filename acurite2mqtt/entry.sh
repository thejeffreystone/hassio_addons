#!/bin/sh

# Exit immediately if a command exits with a non-zero status:
set -e


export LANG=C
PATH="/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"
export LD_LIBRARY_PATH=/usr/local/lib64
CONFIG_PATH=/data/options.json


MQTT_HOST="$(jq --raw-output '.mqtt_host' $CONFIG_PATH)"
MQTT_USERNAME="$(jq --raw-output '.mqtt_user' $CONFIG_PATH)"
MQTT_PASSWORD="$(jq --raw-output '.mqtt_password' $CONFIG_PATH)"

MQTT_TOPIC="$(jq --raw-output '.mqtt_topic' $CONFIG_PATH)"
MQTT_RETAIN="$(jq --raw-output '.mqtt_retain' $CONFIG_PATH)"
PROTOCOL="$(jq --raw-output '.protocol' $CONFIG_PATH)"
DISCOVERY_PREFIX="$(jq --raw-output '.discovery_prefix' $CONFIG_PATH)"
DISCOVERY_INTERVAL="$(jq --raw-output '.discovery_interval' $CONFIG_PATH)"

# Start the listener and enter an endless loop
echo "Starting RTL_433 with parameters:"
echo "MQTT Host =" $MQTT_HOST
echo "MQTT port =" $MQTT_PORT
echo "MQTT User =" $MQTT_USERNAME
echo "MQTT Password =" $MQTT_PASSWORD
echo "MQTT Topic =" $MQTT_TOPIC
echo "MQTT Retain =" $MQTT_RETAIN
echo "PROTOCOL =" $PROTOCOL
echo "DISCOVERY_PREFIX =" $DISCOVERY_PREFIX
echo "DISCOVERY_INTERVAL =" $DISCOVERY_INTERVAL




rtl_433  $PROTOCOL -C si  -F mqtt://$MQTT_HOST:$MQTT_PORT,user=$MQTT_USERNAME,pass=$MQTT_PASSWORD,retain=$MQTT_RETAIN,events=$MQTT_TOPIC/events,states=$MQTT_TOPIC/states,devices=$MQTT_TOPIC[/model][/id][/channel:0]  -M time -M protocol -M level | /scripts/rtl_433_mqtt_hass.py
