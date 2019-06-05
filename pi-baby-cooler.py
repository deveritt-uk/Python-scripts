#!/usr/bin/env python

# This code was originally wrote By Wesley Archer (@raspberrycoulis) with the initial use 
# of turning Phillips Hue bulbs on and off with a light reading from the enviro-pHAT 
# but I have modified it to work with heat and fans. This also sends Pushover notifications to keep users informed.

# Orginal code can be found here: https://github.com/pimoroni/enviro-phat/blob/master/examples/advanced/pi-lluminate.py

# Use the Enviro pHAT to check the temperature in a room, then trigger a webhook to control a smart plug
# via IFTTT. 

# Import the relevant modules

import requests
import time
import datetime
import os
import httplib, urllib
from envirophat import weather

# For Pushover notifications - you'll need to create an app via pushover.net first
APP_TOKEN = 'ADD_YOURS_HERE'    # The app token - required for Pushover
USER_TOKEN = 'ADD_YOURS_HERE'   # Ths user token - required for Pushover

# Get Pushover alerts when the temperature is high - customise the title, message and sound if needed:
def pushover_hot():
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": APP_TOKEN,                         # Insert app token here
        "user": USER_TOKEN,                         # Insert user token here
        "html": "1",                                # 1 for HTML, 0 to disable
        "title": "Fan on!",                    	    # Title of the message
        "message": "<b>It is hot in the baby's room!</b>",      # Content of the message
        "sound": "siren",                           # Define the sound played
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

# Get Pushover alerts when the temperature is cooler - customise the title, message and sound if needed:
def pushover_cold():
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": APP_TOKEN,                         # Insert app token here
        "user": USER_TOKEN,                         # Insert user token here
        "html": "1",                                # 1 for HTML, 0 to disable
        "title": "Fan off!",                    	    # Title of the message
        "message": "<b>It is cooler in the baby's room now!</b>",      # Content of the message
        "sound": "falling",                           # Define the sound played
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

# Get the current time for displaying in the terminal.
def whats_the_time():
    now = datetime.datetime.now()
    return (now.strftime("%H:%M:%S"))

# The function to turn off the fan. Sends a webhook to IFTTT which
# triggers the tplink HS100. Replace the trigger word and tokens from your account.

def turn_off():
    # Set your trigger word - e.g. "cold" - and the IFTTT Webhook token below.
    TRIGGER_WORD = "cold"
    TOKEN = "YOUR IFTTT TOKEN GOES HERE"

    requests.post("https://maker.ifttt.com/trigger/{trigger_word}/with/key/{token}".format(trigger_word=TRIGGER_WORD, token=TOKEN))
    print("Fan off!")

# The function to turn on the fan. Sends a webhook to IFTTT which
# triggers the tplink HS100. Replace the trigger word and tokens from your account.

def turn_on():
    # Set your trigger word - e.g. "hot" - and the IFTTT Webhook token below.
    TRIGGER_WORD = "hot"
    TOKEN = "YOUR IFTTT TOKEN GOES HERE"

    requests.post("https://maker.ifttt.com/trigger/{trigger_word}/with/key/{token}".format(trigger_word=TRIGGER_WORD, token=TOKEN))
    print("Fan on!")

# Check the temperature level and determine whether the fan need to 
# be turned on or off.

def average_temp():
    # Variables for calculating the average temperature levels
    start_time = time.time()
    curr_time = time.time()
    collect_temp_time = 60
    collect_temp_data = []

    # Calculate the average temperature level over 60 seconds
    print("Calculating average temperature...")
    while curr_time - start_time < collect_temp_time:
	      curr_time = time.time()
	      avg = weather.temperature()
	      collect_temp_data.append(avg)
              time.sleep(1)
    # Take the last 45 data points taken over 60 seconds to calculate the average
    average_temperature = sum(collect_temp_data[-45:]) / 45.0
    now = whats_the_time()
    print("Average temperature over {collect_time} seconds is: {average} c*. Last checked at {time}".format(
        collect_time=collect_temp_time,
        average=round(average_temperature,2),
        time=now
    ))
    return average_temperature

try:
    # Local variables.
    state = 0    # Sets the state for the switch
    low = 20	 # Low value for temperature level (celcius).
    high = 24	 # High value for temperature level (celcius).
    period = 120 # Delay, in seconds, between calls.
    while True:
	# Get the average temperature level first:
	room_temperature = average_temp()
	# Now check if the room is warm enough then turn on the fan:
	if room_temperature > high and state != 1:
	    turn_on()
	    pushover_hot()
	    state = 1
	# Or if it is now cool enough, turn off the fan:
	elif room_temperature < low and state == 1:
	    turn_off()
	    pushover_cold()
	    state = 0
	print("Waiting {} seconds before trying again".format(period))
	time.sleep(period)
except KeyboardInterrupt:
    pass
