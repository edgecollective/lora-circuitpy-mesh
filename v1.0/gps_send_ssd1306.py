# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
import time
import board
import busio
import adafruit_rfm9x
import digitalio
import adafruit_gps
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

NODE_ID = 1
#display
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
splash = displayio.Group()
display.show(splash)
text = "Hello World!"
text_area = label.Label(
    terminalio.FONT, text=text, color=0xFFFFFF, x=28, y=HEIGHT // 2 - 1
)
splash.append(text_area)


#setup radio
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)

LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

spi = board.SPI()
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23

counter = 0


uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)

gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")
last_print = time.monotonic()

while True:
    
    gps.update()
    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            print("Waiting for fix...")
            continue
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        lat_str = "{0:.6f}".format(gps.latitude)
        lon_str = "{0:.6f}".format(gps.longitude)
        alt_str = "NA"
        if gps.altitude_m is not None:
            alt_str = str(gps.altitude_m)

        print(lat_str,lon_str,alt_str)
        
        mystring = str(NODE_ID)+","+str(counter)+","+lat_str+","+lon_str+","+alt_str+"\r\n"
        text_area.text="sending:\n"+mystring
        print("sending:",mystring)

        rfm9x.send(bytes(mystring, "utf-8"))
        packet = rfm9x.receive(timeout=3.0)

        if packet is None:
            # Packet has not been received
            LED.value = False
            #print("Received nothing! Listening again...")
            text_area.text="(no reply)"

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
                text_area.text="Received:\n{0}".format(packet_text)
                # Also read the RSSI (signal strength) of the last received message and
                # print it.
                rssi = rfm9x.last_rssi
                print("Received signal strength: {0} dB".format(rssi))
            except:
                print("couldn't parse packet")

        time.sleep(1)
            #rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
            #print("Sent Hello World message!")
        
        counter=counter+1
        
