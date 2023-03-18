# Example to receive addressed packed with ACK and send a response
# Author: Jerry Needell
#
import time
import board
import busio
import digitalio
import adafruit_rfm9x
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import adafruit_bmp280
from analogio import AnalogIn

vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)


def get_voltage(pin):
    return (pin.value * 3.6) / 65536 * 2





displayio.release_displays()

i2c = board.I2C()  # uses board.SCL and board.SDA
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

# Set this to sea level pressure in hectoPascals at your location for accurate altitude reading.
bmp280.sea_level_pressure = 1013.25

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Draw a label
text = ""
stats_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=5, y=10)

text="Waiting..."
incoming_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=5, y=35)
text = ""
outgoing_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00, x=5, y=50)

splash.append(incoming_area)
splash.append(outgoing_area)
splash.append(stats_area)


node_id = 2

# set the time interval (seconds) for sending packets
transmit_interval = 8

# Define radio parameters.
RADIO_FREQ_MHZ = 900.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
# set GPIO pins as necessary - this example is for Raspberry Pi
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)

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
incoming_counter = 0
outgoing_counter = 0

def send(node_to,payload,count):
    rfm9x.destination = node_to
    if rfm9x.send_with_ack(payload):
        print("-->",node_to,payload)
        print("<--",node_to,"ACK")
        rssi = rfm9x.last_rssi
        outgoing_area.text = "--> "+str(node_to)+" ["+str(rssi)+"]"+" ACK "+str(count)
        return(True)
    else:
        print("-->",node_to,payload)
        outgoing_area.text = "--> "+str(node_to)+ " ? " + str(count)
        return(False)

def receive(count):
    packet = rfm9x.receive(with_ack=True, with_header=True)
    if packet is not None:
        node_from = packet[1]
        payload = "{0}".format(packet[4:])
        rssi = rfm9x.last_rssi
        #print("<--",node_from,"("+str(rssi)+")",payload)
        print("<--",node_from,"["+str(rssi)+"]",payload)
        incoming_area.text = "<-- "+str(node_from)+" ["+str(rssi)+"]"+" ACK " + str(count)
        return(packet)
    else:
        return(None)

print("Waiting for packets...")
time_now = time.monotonic()


payload = bytes("heartbeat from node {}".format(rfm9x.node), "UTF-8")


while True:
    packet = receive(incoming_counter)
    if packet is not None:
        # send relayed data from node 1
        payload = packet[4:]
        incoming_counter=incoming_counter+1

    if time.monotonic() - time_now > transmit_interval:
        time_now = time.monotonic()
        # reset the incoming text area, as otherwise it won't be updated
        if send(3,payload,outgoing_counter):
            outgoing_counter=outgoing_counter+1
        payload = bytes("heartbeat from node {}".format(rfm9x.node), "UTF-8")
        print("Barometric pressure:", bmp280.pressure)
        print("Altitude: {:.1f} m".format(bmp280.altitude))
        battery_voltage = get_voltage(vbat_voltage)
        stats_area.text="{:.0f} hP  {:.2f} V".format(bmp280.pressure,battery_voltage)

