#!/usr/bin/env python3
# coding=utf-8

"""MQTT Home Assistant auto discovery for rtl_433 events."""

# It is strongly recommended to run rtl_433 with "-C si" and "-M newmodel".

# Needs Paho-MQTT https://pypi.python.org/pypi/paho-mqtt

# Option: PEP 3143 - Standard daemon process library
# (use Python 3.x or pip install python-daemon)
# import daemon

import json
import os
import time
import paho.mqtt.client as mqtt
# from datetime import datetime

MQTT_HOST = os.environ['MQTT_HOST']
MQTT_PORT = os.environ['MQTT_PORT']
MQTT_USERNAME = os.environ['MQTT_USERNAME']
MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
MQTT_TOPIC = os.environ['MQTT_TOPIC']
DISCOVERY_PREFIX = os.environ['DISCOVERY_PREFIX']
DISCOVERY_INTERVAL = os.environ['DISCOVERY_INTERVAL']
DEBUG = False

# Convert number environment variables to int
MQTT_PORT = int(MQTT_PORT)
DISCOVERY_INTERVAL = int(DISCOVERY_INTERVAL)

discovery_timeouts = {}

# Fields used for creating topic names
NAMING_KEYS = [ "type", "model", "subtype", "channel", "id" ]

# Fields that get ignored when publishing to Home Assistant
# (reduces noise to help spot missing field mappings)
SKIP_KEYS = NAMING_KEYS + [ "time", "mic", "mod", "freq", "sequence_num",
                            "message_type", "exception", "raw_msg" ]

mappings = {
    "temperature_C": {
        "device_type": "sensor",
        "object_suffix": "T",
        "config": {
            "device_class": "temperature",
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
            "name": "Temperature",
            "unit_of_measurement": "°F",
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
            "value_template": "{{ float(value|int) * 99 + 1 }}"
        }
    },

    "humidity": {
        "device_type": "sensor",
        "object_suffix": "H",
        "config": {
            "device_class": "humidity",
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
            "name": "Pressure",
            "unit_of_measurement": "hPa",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_speed_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "device_class": "weather",
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_km_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "name": "Wind Speed",
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_mi_h": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "name": "Wind Speed",
            "unit_of_measurement": "mi/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_avg_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
            "name": "Wind Average",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 | round(2) }}"
        }
    },

    "wind_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "WS",
        "config": {
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
            "unit_of_measurement": "km/h",
            "value_template": "{{ value|float }}"
        }
    },

    "wind_max_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
            "name": "Wind max",
            "unit_of_measurement": "km/h",
            "value_template": "{{ float(value|float) * 3.6 | round(2) }}"
        }
    },

    "gust_speed_m_s": {
        "device_type": "sensor",
        "object_suffix": "GS",
        "config": {
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
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_mm_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ value|float }}"
        }
    },

    "rain_in": {
        "device_type": "sensor",
        "object_suffix": "RT",
        "config": {
            "name": "Rain Total",
            "unit_of_measurement": "mm",
            "value_template": "{{ float(value|float) * 25.4 | round(2) }}"
        }
    },

    "rain_rate_in_h": {
        "device_type": "sensor",
        "object_suffix": "RR",
        "config": {
            "name": "Rain Rate",
            "unit_of_measurement": "mm/h",
            "value_template": "{{ float(value|float) * 25.4 | round(2) }}"
        }
    },

    "tamper": {
        "device_type": "binary_sensor",
        "object_suffix": "tamper",
        "config": {
            "device_class": "safety",
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
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "snr": {
        "device_type": "sensor",
        "object_suffix": "snr",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "noise": {
        "device_type": "sensor",
        "object_suffix": "noise",
        "config": {
            "device_class": "signal_strength",
            "unit_of_measurement": "dB",
            "value_template": "{{ value|float|round(2) }}"
        }
    },

    "depth_cm": {
        "device_type": "sensor",
        "object_suffix": "D",
        "config": {
            "device_class": "depth",
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
            "name": "Outside Luminancee",
            "unit_of_measurement": "lux",
            "value_template": "{{ value|int }}"
        }
    },

    "uv": {
        "device_type": "sensor",
        "object_suffix": "uv",
        "config": {
            "name": "UV Index",
            "unit_of_measurement": "UV Index",
            "value_template": "{{ value|int }}"
        }
    },

    "storm_dist": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}"
        }
    },

    "strike_distance": {
        "device_type": "sensor",
        "object_suffix": "stdist",
        "config": {
            "name": "Lightning Distance",
            "unit_of_measurement": "mi",
            "value_template": "{{ value|int }}"
        }
    },

    "strike_count": {
        "device_type": "sensor",
        "object_suffix": "strcnt",
        "config": {
            "name": "Lightning Strike Count",
            "value_template": "{{ value|int }}"
        }
    },
}


def mqtt_connect(client, userdata, flags, rc):
    """Callback for MQTT connects."""
    print("MQTT connected: " + mqtt.connack_string(rc))
    client.publish("/".join([MQTT_TOPIC, "status"]), payload="online", qos=0, retain=True)
    if rc != 0:
        print("Could not connect. Error: " + str(rc))
    else:
        client.subscribe("/".join([MQTT_TOPIC, "events"]))


def mqtt_disconnect(client, userdata, rc):
    """Callback for MQTT disconnects."""
    print("MQTT disconnected: " + mqtt.connack_string(rc))


def mqtt_message(client, userdata, msg):
    """Callback for MQTT message PUBLISH."""
    try:
        # Decode JSON payload
        data = json.loads(msg.payload.decode())
        # print("DATA  ", data)
        topicprefix = "/".join(msg.topic.split("/", 2)[:2])
        bridge_event_to_hass(client, topicprefix, data)
        if DEBUG:
            print("{} : {}".format(topicprefix, data))

    except json.decoder.JSONDecodeError:
        print("JSON decode error: " + msg.payload.decode())
        return


def sanitize(text):
    """Sanitize a name for Graphite/MQTT use."""
    return (text
            .replace(" ", "_")
            .replace("/", "_")
            .replace(".", "_")
            .replace("&", ""))

def rtl_433_device_topic(data):
    """Return rtl_433 device topic to subscribe to for a data element"""

    path_elements = []

    for key in NAMING_KEYS:
        if key in data:
            element = sanitize(str(data[key]))
            path_elements.append(element)

    return '/'.join(path_elements)

def publish_config(mqttc, topic, model, instance, mapping):
    """Publish Home Assistant auto discovery data."""
    global discovery_timeouts

    instance_no_slash = instance.replace("/", "-")
    device_type = mapping["device_type"]
    object_suffix = mapping["object_suffix"]
    object_id = instance_no_slash
    object_name = "-".join([object_id,object_suffix])

    path = "/".join([DISCOVERY_PREFIX, device_type, object_id, object_name, "config"])

    # check timeout
    now = time.time()
    if path in discovery_timeouts:
        if discovery_timeouts[path] > now:
            return False

    discovery_timeouts[path] = now + DISCOVERY_INTERVAL

    config = mapping["config"].copy()
    config["name"] = object_name
    config["state_topic"] = topic
    config["unique_id"] = object_name
    config["device"] = { "identifiers": object_id, "name": object_id, "model": model, "manufacturer": "rtl_433" }

    if DEBUG:
        print(path,":",json.dumps(config))

    mqttc.publish(path, json.dumps(config), qos=0, retain=True)

    return True



def bridge_event_to_hass(mqttc, topicprefix, data):
    """Translate some rtl_433 sensor data to Home Assistant auto discovery."""

    if "model" not in data:
        # not a device event
        return

    model = sanitize(data["model"])

    skipped_keys = []
    published_keys = []

    instance = rtl_433_device_topic(data)
    if not instance:
        # no unique device identifier
        if DEBUG:
            print("No suitable identifier found for model: ", model)
        return

    # detect known attributes
    for key in data.keys():
        if key in mappings:
            # topic = "/".join([topicprefix,"devices",model,instance,key])
            topic = "/".join([topicprefix,"devices",instance,key])
            if publish_config(mqttc, topic, model, instance, mappings[key]):
                published_keys.append(key)
        else:
            if key not in SKIP_KEYS:
                skipped_keys.append(key)

    if published_keys and DEBUG:
        print("Published %s: %s" % (instance, ", ".join(published_keys)))

        if skipped_keys and DEBUG:
            print("Skipped %s: %s" % (instance, ", ".join(skipped_keys)))


def rtl_433_bridge():
    """Run a MQTT Home Assistant auto discovery bridge for rtl_433."""
    mqttc = mqtt.Client()
    mqttc.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqttc.on_connect = mqtt_connect
    mqttc.on_disconnect = mqtt_disconnect
    mqttc.on_message = mqtt_message

    mqttc.will_set("/".join([MQTT_TOPIC, "status"]), payload="offline", qos=0, retain=True)
    mqttc.connect_async(MQTT_HOST, MQTT_PORT, 60)
    mqttc.loop_start()

    while True:
        time.sleep(1)


def run():
    """Run main or daemon."""
   
    rtl_433_bridge()


if __name__ == "__main__":

    run()