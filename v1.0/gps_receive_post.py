# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# Author: Tony DiCola
import board
import busio
import digitalio
import time
import adafruit_rfm9x
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

JSON_POST_URL = "http://bayou.pvos.org/data/"+secrets["public_key"]

print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

attempts = 3  # Number of attempts to retry each request
failure_count = 0
response = None

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)
# Or uncomment and instead use these if using a Feather M0 RFM9x board and the appropriate
# CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
#spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi = board.SPI()

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.


# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 252 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")

while True:
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        #print("Received nothing! Listening again...")
    else:
        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text=None
        try:
            packet_text = str(packet, "ascii")
            print("Received (ASCII): {0}".format(packet_text))
            # Also read the RSSI (signal strength) of the last received message and
            # print it.
            rssi = rfm9x.last_rssi
            print("Received signal strength: {0} dB".format(rssi))

            time.sleep(1)
            rfm9x.send(bytes("Node 0\r\n", "utf-8"))
            print("Sent Hello World message!")
        except:
            print("couldn't parse packet")

        # now send over wifi
        #gps_lat, gps_lon, gps_alt
        if packet_text is not None:
            rdata = packet_text.split(",")
            print("packet_text_split=",packet_text.split(","))

            node_id = rdata[0]
            send_count = rdata[1]
            gps_lat = str(rdata[2])
            gps_lon = str(rdata[3])
            gps_alt = str(rdata[4])

            print("gps_lat:",gps_lat)
            print("gps_lon:",gps_lon)

            json_data = {"private_key": secrets["private_key"], "gps_lat":gps_lat,"gps_lon":gps_lon,"gps_alt":gps_alt,"node_id":node_id,"rssi":rssi}
            print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
            try:
                response = requests.post(JSON_POST_URL, json=json_data)
                print("response:",response.text)
                response.close()
            except:
                print("post failed")
            
            time.sleep(3)
