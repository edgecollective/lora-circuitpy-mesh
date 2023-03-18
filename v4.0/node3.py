# Example to receive addressed packed with ACK and send a response
# Author: Jerry Needell
#
import time
import board
import busio
import digitalio
import adafruit_rfm9x

node_id = 3

# set the time interval (seconds) for sending packets
transmit_interval = 8

# Define radio parameters.
RADIO_FREQ_MHZ = 900.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
# set GPIO pins as necessary - this example is for Raspberry Pi
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D7)

# Initialize SPI bus.
spi = board.SPI()
# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# identity of this node
rfm9x.node = node_id
# enable CRC checking
rfm9x.enable_crc = True
# set delay before transmitting ACK (seconds)
rfm9x.ack_delay = 0.1
# set node addresses

# initialize counter
counter = 0
ack_failed_counter = 0

def send(node_to,payload):
    rfm9x.destination = node_to
    if rfm9x.send_with_ack(payload):
        print("-->",node_to,payload)
        print("<--",node_to,"ACK")
    else:
        print("-->",node_to,payload)

def receive():
    packet = rfm9x.receive(with_ack=True, with_header=True)
    if packet is not None:
        node_from = packet[1]
        payload = "{0}".format(packet[4:])
        rssi = rfm9x.last_rssi
        #print("<--",node_from,"("+str(rssi)+")",payload)
        print("<--",node_from,"["+str(rssi)+"]",payload)
        return(packet)
    else:
        return(None)

print("Waiting for packets...")
time_now = time.monotonic()

while True:
    packet = receive()
    #if time.monotonic() - time_now > transmit_interval:
    #    time_now = time.monotonic()