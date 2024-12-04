#!/usr/bin/env python3
# coding=utf-8

"""MQTT Home Assistant auto discovery for rtl_433 events."""

# It is strongly recommended to run rtl_433 with "-C si" and "-M newmodel".

# Needs Paho-MQTT https://pypi.python.org/pypi/paho-mqtt

# Option: PEP 3143 - Standard daemon process library
# (use Python 3.x or pip install python-daemon)
# import daemon

from __future__ import print_function, with_statement

import json
import os
import time
import paho.mqtt.client as mqtt
import logging
from datetime import datetime

MQTT_HOST = os.environ['MQTT_HOST']
MQTT_PORT = os.environ['MQTT_PORT']
MQTT_USERNAME = os.environ['MQTT_USERNAME']
MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
MQTT_TOPIC = os.environ['MQTT_TOPIC']
DISCOVERY_PREFIX = os.environ['DISCOVERY_PREFIX']
WHITELIST_ENABLE = os.environ['WHITELIST_ENABLE']
WHITELIST = os.environ['WHITELIST']
DISCOVERY_INTERVAL = os.environ['DISCOVERY_INTERVAL']
AUTO_DISCOVERY = os.environ['AUTO_DISCOVERY']
DEBUG = os.environ['DEBUG']
EXPIRE_AFTER = os.environ['EXPIRE_AFTER']
MQTT_RETAIN = os.environ['MQTT_RETAIN']
# Convert number environment variables to int
MQTT_PORT = int(MQTT_PORT)
DISCOVERY_INTERVAL = int(DISCOVERY_INTERVAL)

discovery_timeouts = {}

whitelist_list = WHITELIST.split()
blocked = []
rate_limited = {}

if DEBUG == "true":
    LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
else:
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

if WHITELIST_ENABLE == "true":
    whitelist_on = True
else:
    whitelist_on = False

if AUTO_DISCOVERY == "true":
    auto_discovery  = True
else:
    auto_discovery  = False

mappings = {
    "time": {
        "device_type": "sensor",
        "object_suffix": "last_seen",
        "config": {
            "device_class": "timestamp",
            "entity_category": "diagnostic",
            "name": "last_seen",
            "value_template": "{{ value }}"
        }
    },
    "freq": {
        "device_type": "sensor",
        "object_suffix": "freq",
        "config": {
            "device_class": "frequency",
            "entity_category": "diagnostic",
            "name": "frequency",
            "unit_of_measurement": "MHz",
            "value_template": "{{ value }}"
        }
    },
    "channel": {
        "device_type": "sensor",
        "object_suffix": "channel",
        "config": {
            "device_class": "enum",
            "name": "device_channel",
            "options": ["A", "B", "C"],
            "entity_category": "diagnostic",
            "value_template": "{{ value }}"
        }
    },
    "temperature_C": {
        "device_type": "sensor",
        "object_suffix": "T",
        "config": {
            "device_class": "temperature",
            "state_class":"measurement",
            "name": "Temperature",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float }}"
        }
    },
    "temperature_1_C": {
        "device_type": "sensor",
        "object_suffix": "T1",
        "config": {
            "device_class": "temperature",
            "state_class":"measurement",
            "name": "Temperature 1",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float }}"
        }
    },
    "temperature_2_C": {
        "device_type": "sensor",
        "object_suffix": "T2",
        "config": {
            "device_class": "temperature",
            "state_class":"measurement",
            "name": "Temperature 2",
            "unit_of_measurement": "°C",
            "value_template": "{{ value|float }}"
        }
    },
    "temperature_F": {
        "device_type": "sensor",
        "object_suffix": "F",
        "config": {
            "device_class": "temperature",
            "state_class":"measurement",
            "name": "Temperature",
            "unit_of_measurement": "°F",
            "assumed_state" : "True",
            "value_template": "{{ value|float }}"
        }
    },
     "temperature_1_F": {
        "device_type": "sensor",
        "object_suffix": "F",
        "config": {
            "device_class": "temperature",
            "name": "Temperature 1",
            "unit_of_measurement": "°F",
            "assumed_state" : "True",
            "value_template": "{{ value|float }}"
        }
    },
    "temperature_2_F": {
        "device_type": "sensor",
        "object_suffix": "F",
        "config": {
            "device_class": "temperature",
            "state_class":"measurement",
            "name": "Temperature 2",
            "unit_of_measurement": "°F",
            "assumed_state" : "True",
            "value_template": "{{ value|float }}"
        }
    },

    "battery_ok": {
        "device_type": "sensor",
        "object_suffix": "B",
        "config": {
            "device_class": "battery",
            "name": "Battery",
            "unit_of_measurement": "%",
            "value_template": "{{ float(value) * 99 + 1 | int }}"
        }
    },

    "humidity": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
            "state_class":"measurement",
            "name": "Humidity",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}"
        }
    },

    "moisture": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
            "state_class":"measurement",
            "name": "Moisture",
            "unit_of_measurement": "%",
            "value_template": "{{ value|float }}"
        }
    },

    "pressure_hPa": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "state_class":"measurement",
            "name": "Pressure",
            "unit_of_measurement": "hPa",
            "value_template": "{{ value|float }}"
        }
    },

    "pressure_kPa": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "state_class":"measurement",
            "name": "Pressure",
            "unit_of_measurement": "kPa",
            "value_template": "{{ value|float }}"
        }
    },
    
    "pressure_inHg": {
        "device_type": "sensor",
        "object_suffix": "P",
        "config": {
            "device_class": "pressure",
            "state_class":"measurement",
            "name": "Pressure",
            "unit_of_measurement": "inHg",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "state_class":"measurement",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_mi_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "state_class":"measurement",
            "name": "Wind Speed",
            "unit_of_measurement": "mph",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "state_class":"measurement",
            "name": "Wind Average",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 | round(2) }}"
        }
    },

    "wind_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "wind_speed",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 }}"
        }
    },

    "gust_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "name": "Gust Speed",
            "device_class": "wind_speed",
            "state_class":"measurement",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_max_km_h": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "name": "Wind max",
            "device_class": "wind_speed",
            "state_class":"measurement",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_max_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "state_class":"measurement",
            "name": "Wind max",
            "unit_of_measurement": "m/s",
            "value_template": "{{ float(value|float) * 3.6 | round(2) }}"
        }
    },

    "gust_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "device_class": "wind_speed",
            "state_class":"measurement",
            "name": "Gust Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 }}"
        }
    },

    "wind_dir_deg": {
        "device_type": "sensor",
        "object_suffix": "WD",
        "config": {
            "name": "Wind Direction",
            "unit_of_measurement": "°",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_mm": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "device_class": "precipitation",
            "state_class":"total_increasing",
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_mm_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "device_class": "precipitation_intensity",
            "state_class":"measurement",
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_in": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "device_class": "precipitation",
            "state_class":"total_increasing",
            "name": "Rain Total",
            "unit_of_measurement": "in",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_rate_in_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "device_class": "precipitation_intensity",
            "state_class":"measurement",
            "name": "Rain Rate",
            "unit_of_measurement": "in/h",
            "value_template": "{{ value|float }}"
        }
    },

    "tamper": {
        "device_type": "binary_sensor",
        "object_suffix": "tamper",
        "config": {
            "device_class": "safety",
            "entity_category": "diagnostic",
            "force_update": "true",
            "payload_on": "1",
            "payload_off": "0"
        }
    },

    "alarm": {
        "device_type": "binary_sensor",
        "object_suffix": "alarm",
        "config": {
            "device_class": "safety",
            "force_update": "true",
            "payload_on": "1",
            "payload_off": "0"
        }
    },

    "rssi": {
        "device_type": "sensor",
        "object_suffix": "rssi",
        "config": {
            "device_class": "signal_strength",
            "state_class":"measurement",
            "unit_of_measurement": "dB",
            "entity_category": "diagnostic",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "snr": {
        "device_type": "sensor",
        "object_suffix": "snr",
        "config": {
            "device_class": "signal_strength",
            "state_class":"measurement",
            "entity_category": "diagnostic",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "noise": {
        "device_type": "sensor",
        "object_suffix": "noise",
        "config": {
            "device_class": "signal_strength",
            "state_class":"measurement",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "depth_cm": {
        "device_type": "sensor",
        "object_suffix": "D",
        "config": {
            "state_class":"measurement",
            "name": "Depth",
            "unit_of_measurement": "cm",
            "value_template": "{{ value|float }}"
        }
    },

    "power_W": {
        "device_type": "sensor",
        "object_suffix": "watts",
        "config": {
            "device_class": "power",
            "state_class":"measurement",
            "name": "Power",
            "unit_of_measurement": "W",
            "value_template": "{{ value|float }}"
        }
    },

    "lux": {
        "device_type": "sensor",
        "object_suffix": "lux",
        "config": {
            "device_class": "illuminance",
            "state_class":"measurement",
            "name": "Outside Luminancee",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}"
        }
    },

    "light_klx": {
        "device_type": "sensor",
        "object_suffix": "light_klx",
        "config": {
            "device_class": "illuminance",
            "name": "Outside Luminancee",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}"
        }
    },

    "brightness": {
        "device_type": "sensor",
        "object_suffix": "lux",
        "config": {
            "device_class": "illuminance",
            "state_class":"measurement",
            "name": "Brightness",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}"
        }
    },

    "uv": {
        "device_type": "sensor",
        "object_suffix": "uv",
        "config": {
            "device_class": "irradiance",
            "state_class":"measurement",
            "name": "UV Index",
            "unit_of_measurement": "UV Index",
            "value_template": "{{ value|int }}"
        }
    },

    "storm_dist": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "device_class":"distance",
            "state_class":"measurement",
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}"
        }
    },

    "strike_distance": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "device_class":"distance",
            "state_class":"measurement",
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}"
        }
    
    },
    "consumption": {
        "device_type": "meter",
        "object_suffix": "meter",
        "config": {
            "device_class": "gas",
            "name": "meter",
            "unit_of_measurement": "ft³",
            "value_template": "{{ value|float }}"
        }
    },
    "strike_count": {
        "device_type": "sensor",
        "object_suffix": "strcnt",
        "config": {
            "name": "Lightning Strike Count",
            "state_class":"total_increasing",
            "value_template": "{{ value|int }}"
        }
    },

    "detect_wet": {
        "device_type": "binary_sensor",
        "object_suffix": "detect_wet",
        "config": {
            "device_class": "moisture",
            "entity_category": "diagnostic",
            "force_update": "true",
            "payload_on": "1",
            "payload_off": "0"
        }
    },
    "event": {
        "device_type": "sensor",
        "object_suffix": "event",
        "config": {
            "device_class": "enum",
            "name": "event",
            "options": ["Button Press", "Water Leak", "Battery Low"],
            "entity_category": "diagnostic",
            "value_template": "{{ value }}"
        }

}


def mqtt_connect(client, userdata, flags, rc):
    """Callback for MQTT connects."""
    print("MQTT connected: " + mqtt.connack_string(rc))
    client.publish("/".join([MQTT_TOPIC, "status"]), payload="online", qos=0, retain=True)
    if rc != 0:
        logging.critical("Could not connect. Error: " + str(rc))
    else:
        client.subscribe("/".join([MQTT_TOPIC, "events"]))


def mqtt_disconnect(client, userdata, rc):
    """Callback for MQTT disconnects."""
    logging.critical("MQTT disconnected: " + mqtt.connack_string(rc))


def mqtt_message(client, userdata, msg):
    """Callback for MQTT message PUBLISH."""
    try:
        # Decode JSON payload
        data = json.loads(msg.payload.decode())
        logging.debug("Received Device Data from SDR and sent to MQTT: {} : {}".format(msg.topic, json.dumps(data)))
        bridge_event_to_hass(client, msg.topic, data)

    except json.decoder.JSONDecodeError:
        logging.warning("JSON decode error: " + msg.payload.decode())
        return


def sanitize(text):
    """Sanitize a name for Graphite/MQTT use."""
    return (text
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("&", ""))


def publish_config(mqttc, topic, model, instance, channel, mapping):
    """Publish Home Assistant auto discovery data."""
    global discovery_timeouts

    device_type = mapping["device_type"]
    object_id = "_".join([model.replace("-", "_"), instance])
    object_suffix = mapping["object_suffix"]

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, object_suffix, "config"])

    # check timeout
    now = time.time()
    if path in discovery_timeouts:
        if discovery_timeouts[path] > now:
            return

    discovery_timeouts[path] = now + DISCOVERY_INTERVAL

    config = mapping["config"].copy()
    config["state_topic"] = "/".join([MQTT_TOPIC, model, instance, channel, topic])
    config["name"] = " ".join([model.replace("-", " "), instance, object_suffix])
    config["unique_id"] = "".join(["rtl433", device_type, instance, object_suffix])
    config["availability_topic"] = "/".join([MQTT_TOPIC, "status"])
    config["expire_after"] = EXPIRE_AFTER

    # add Home Assistant device info

     # Check for missing manufacturer info
    if '-' in model:
        manufacturer, model = model.split("-", 1)
    else:
        manufacturer = 'Unknown'

    device = {}
    device["identifiers"] = instance
    device["name"] = instance
    device["model"] = model
    device["manufacturer"] = manufacturer
    config["device"] = device

    mqttc.publish(path, json.dumps(config),  qos=0, retain=True)
    logging.debug("Device Config was saved to {} : {}".format(path,json.dumps(config)))
           

def bridge_event_to_hass(mqttc, topic, data):
    """Translate some rtl_433 sensor data to Home Assistant auto discovery."""

    if "model" not in data:
        # not a device event
        return
    model = sanitize(data["model"])

    if "id" in data:
        instance = str(data["id"])
    else:
        instance = 0
        
    if instance == 0:
        logging.warning("Device Id:{} doesn't appear to be a actual device. Skipping..".format(data['id']))
        return
        
    if "channel" in data:
        channel = str(data["channel"])
    else:
        channel = 'A'

    device = '{}-{}'.format(data['id'],data['model'])
     
    if (whitelist_on == True) and (instance not in whitelist_list):
        # Let's reduce the noise in the log and hide the duplicate notifications.
        if (instance not in blocked):
            logging.info("Device Id:{} Model: {} not in whitelist. Add to the Whitelist to create device in Home Assistant.".format(data['id'],data['model']))
        blocked.append('{}'.format(data['id']))
        return

    if (auto_discovery == True):
        # Let's reduce the noise in the log and hide the duplicate notifications.
        if (device not in rate_limited) or ( (datetime.now() - rate_limited[device]).seconds > 30 ):
            logging.debug('Device: {} - Creating/Updating device config in Home Assistant for Auto discovery.'.format(device))
        rate_limited[device] = datetime.now()
        # detect known attributes
        for key in data.keys():
            if key in mappings:
                publish_config(mqttc, key, model, instance, channel, mappings[key])
              


def rtl_433_bridge():
    """Run a MQTT Home Assistant auto discovery bridge for rtl_433."""
    logging.basicConfig(format='%(levelname)s:%(message)s', level=LOGLEVEL)
    
    mqttc = mqtt.Client()
    mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttc.on_connect = mqtt_connect
    mqttc.on_disconnect = mqtt_disconnect
    mqttc.on_message = mqtt_message

    mqttc.will_set("/".join([MQTT_TOPIC, "status"]), payload="offline", qos=0, retain=True)
    mqttc.connect_async(MQTT_HOST, MQTT_PORT, 60)
    mqttc.loop_start()

    logging.info('Started')

    while True:
        time.sleep(1)


def run():
    """Run main or daemon."""
    # with daemon.DaemonContext(files_preserve=[sock]):
    #  detach_process=True
    #  uid
    #  gid
    #  working_directory
    rtl_433_bridge()


if __name__ == "__main__":

    run()
