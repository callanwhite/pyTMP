#!/usr/bin/env python
import time
import os
import RPi.GPIO as GPIO
 
# The code below is a bitbanged implementation
# for use with the MCP3008 ADC chip. 
# This is provided by Adafruit and can be found
# at https://gist.github.com/ladyada/3151375#file-adafruit_mcp3008-py
# The MCP3008 gives a binary representation of an
# analogue input.
 
GPIO.setmode(GPIO.BCM)
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
 
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)


# /////////////////////////
# END ADAFRUIT MCP3008 CODE
# /////////////////////////

def bin2temp(adcout):
	#adcout is the binary representation provided by the mcp3008 chip
	#since we're using the 3.3v line, 0=0v and 1024=3.3v
	#first convert the binary to its voltage equivalent
	volts = (3.3/1024.0) * adcout
	
	#datasheet for tmp36 http://dlnmh9ip6v2uc.cloudfront.net/datasheets/Sensors/Temp/TMP35_36_37.pdf
	#describes a 0.5v offset in order to deal with negative values (operates from -40c to +125c)
	volts = (volts - 0.5) * 1000.0
	
	#the tmp36 outputs 10mV per degree celsius so devide the result by 10
	temp = volts / 10.0
	return temp
	
def c2f(temp):
	return (temp*1.8)+32

def c2k(temp):
	return temp+273.0
	
def current_temp():
	return bin2temp(readadc(0,SPICLK,SPIMOSI,SPIMISO,SPICS))

# while True:
	# try:
		# temp = bin2temp(readadc(0,SPICLK,SPIMOSI,SPIMISO,SPICS))
		# print("Celsius: {}\tFahrenheit: {}\tKelvin:{}".format(temp,c2f(temp),c2k(temp)))
		# time.sleep(1)
	# except KeyboardInterrupt:
	#clean up
		# GPIO.cleanup()
	
