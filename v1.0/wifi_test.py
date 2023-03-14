# SPDX-FileCopyrightText: 2020 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import time

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

JSON_POST_URL = "http://bayou.pvos.org/data/"+secrets["public_key"]


print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()

print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

attempts = 3  # Number of attempts to retry each request
failure_count = 0
response = None

while True:

    json_data = {"private_key": secrets["private_key"], "node_id":1,"temperature_c":23.0}
    print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
    try:
        response = requests.post(JSON_POST_URL, json=json_data)
        print("response:",response.text)
        response.close()
    except:
        print("post failed")

    #response.close()

    time.sleep(2)

#json_resp = response.json()

#print(json_resp)

#print("done")
