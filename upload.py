#!/usr/bin/env python

import os
import xively
import datetime
import time
import tmp36
import RPi.GPIO as GPIO
import requests

FEED_ID = #insert your feed id
API_KEY = "INSERT YOUR KEY HERE"

api = xively.XivelyAPIClient(API_KEY)
GPIO.setmode(GPIO.BCM)
#BCM representation of GPIO pin used for LED
LED = 17
GPIO.setup(LED, GPIO.OUT)

def read_temp():
	return tmp36.current_temp()


def get_datastream(feed):
	try:
		datastream = feed.datastreams.get("TMP36")
		print "Found data stream"
		return datastream
	except:
		print "Creating new datastream"
		datastream = feed.datastreams.create("TMP36",tags="tmp36_01")
		return datastream

def run(datastream):
	print "Starting upload script"
	#feed = api.feeds.get(FEED_ID)
	#datastream = get_datastream(feed)
	temp = read_temp()
	print "Uploading temp"
	datastream.current_value = temp
	datastream.at = datetime.datetime.utcnow()
	try:
		datastream.update()
		GPIO.output(LED,True)
		time.sleep(0.5)
		GPIO.output(LED,False)
	except requests.exceptions.HTTPError as e:
		print "HTTPError({}): {1}".format(e.errno, e.strerror)
		
	time.sleep(5)

try:
	feed = api.feeds.get(FEED_ID)
	datastream = get_datastream(feed)
	while True:
		run(datastream)
except KeyboardInterrupt:
	GPIO.output(LED,False)
	GPIO.cleanup()
