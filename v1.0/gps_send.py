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
        
        mystring = str(counter)+","+lat_str+","+lon_str+","+alt_str+"\r\n"
        rfm9x.send(bytes(mystring, "utf-8"))
        print("Sent:",mystring)
        counter=counter+1
        
