#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'marcel'

from mpd import MPDClient
from mpd import ConnectionError as MPDConnectionError
from lib.photocell.photocell import CheckLight
from lib.mpd_lcd.lcd_controller import LCD
from lib.mpd_lcd.locale_de import LocaleDE
from lib.mpd_lcd.line_controller import TimeLine, MPDLine, FetchLine
import logging

# Setup logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename="flushfm.log", level="DEBUG", filemode="w")
logging.info("Log started")

# MPD Client
client = MPDClient()

client.timeout = 10
client.idletimeout = None

def client_connect():
	logging.info("Attempt to (re-)connect to mpd server")
	client.connect("localhost", 6600)
	logging.info("Finished attempt to (re-)connect to mpd server")
	logging.info(client.status)

client_connect()

# LCD
locale_de = LocaleDE()

lcd = LCD(4, 20, locale = locale_de)
logging.info("Setup LCD with 4 lines, 20 columns and locale_de")

lcd.set_line("time", TimeLine(lcd, 1))
logging.info("Line 1: TimeLine")
lcd.set_line("station", MPDLine(lcd, 2, "name", align='c', refresh_interval=10, step_interval=1))
logging.info("Line 2: MPDLine (name)")
lcd.set_line("song", MPDLine(lcd, 3, "title"))
logging.info("Line 3: MPDLine (title)")
lcd.set_line("proverb", FetchLine(lcd, 4, "http://sprichwortgenerator.de/plugin.php"))
logging.info("Line 4: Fetch Proverb")

# init
lcd.line_container["time"].run_every()
lcd.line_container["station"].run_every()
lcd.line_container["song"].run_every()
lcd.line_container["proverb"].run_every()


# define methods to run when light state changes
def light_on_method():
	logging.info("Try to resume MPD client.")
	try:
		client.play()
	except MPDConnectionError:
		logging.info("Lost MPD connection")
	
		client_connect()
		client.play()

	logging.info("Try to resume LCD.")
	lcd.resume()


def light_off_method():
	logging.info("Try to stop MPD client.")
	try:
		client.stop()
	except MPDConnectionError:
		logging.info("Lost MPD connection")

		client_connect()
		client.stop()

	logging.info("Try to standby LCD.")
	lcd.standby()

# Check light
check_light = CheckLight(light_on_method, light_off_method)
check_light.start()
