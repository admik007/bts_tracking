import paho.mqtt.client as mqtt
import json
import random
from urllib.parse import parse_qs

MQTT_SERVER = "192.168.10.1"
MQTT_TOPICS = ["pico/data", "pico/gps"]
JSON_FILE = "/var/www/html/firmware/data.json"

# store latest device info
devices = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    for topic in MQTT_TOPICS:
        client.subscribe(topic)

def parse_gps_payload(payload):
    """
    Parse GPS payload of the form:
    lat=48.71951&lon=21.20799&alt=342&time=2025-12-07T17:47:25Z
    Returns a dict with float lat/lon, alt (string or float), and time.
    """
    # replace & with & to work with parse_qs
    parts = parse_qs(payload.replace("&", "&"))
    gps = {}
    try:
        gps["lat"] = float(parts.get("lat", [0])[0])
        gps["lon"] = float(parts.get("lon", [0])[0])
        gps["alt"] = parts.get("alt", [""])[0]
        gps["gps_time"] = parts.get("time", [""])[0]
    except Exception as e:
        print("Error parsing GPS:", e)
    return gps


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        if msg.topic == "pico/data":
            data = {}
            pairs = payload.split(",")
            for p in pairs:
                if "=" in p:
                    k, v = p.split("=", 1)
                    data[k.strip()] = v.strip()

            dev = data.get("dev")
            if dev:
                if dev not in devices:
                    devices[dev] = {}
                for key in ["dev","mcc","mnc","bsic","cid","lac","rtc","ip"]:
                    if key in data:
                        devices[dev][key] = data[key]

        elif msg.topic == "pico/gps":
            gps_data = parse_gps_payload(payload)

            # add unique random offset for each device
            for dev in devices:
                lat_offset = random.uniform(0.00002, 0.00009)
                lon_offset = random.uniform(0.00002, 0.00009)

                devices[dev].update({
                    "lat": round(gps_data["lat"] + lat_offset, 8),
                    "lon": round(gps_data["lon"] + lon_offset, 8),
                    "alt": gps_data["alt"],
                    "gps_time": gps_data["gps_time"]
                })

        # write JSON file
        with open(JSON_FILE, "w") as f:
            # only save devices with a valid CellID
            filtered_devices = [d for d in devices.values() if "cid" in d and d["cid"]]
            json.dump(filtered_devices, f, indent=2)

    except Exception as e:
        print("Error processing message:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()
