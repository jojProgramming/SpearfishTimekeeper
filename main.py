import luma.oled
import bme680
import requests
from PIL.ImageFont import ImageFont
from luma.core.mixin import capabilities

"""
An analog clockface with date & time.

Ported from:
https://gist.github.com/TheRayTracer/dd12c498e3ecb9b8b47f#file-clock-py
"""

import time, sys
import datetime
from options import get_device, getLoc
from luma.core.render import canvas
from PIL import ImageFont
import feedparser

#TEMP ONLY
from subprocess import PIPE, Popen

textArray = []
sensor = bme680.BME680()



def main():
	today_last_time = "Unknown"
	today_last_minute = "Unknown"
	display_mode = "TEMP"
	last_weather_check = datetime.datetime.now() - datetime.timedelta(hours=2)
	cx = 5
	modes = ["ADVANCED", "TEMPERATURE", "HUMIDITY", "PRESSURE"]
	doWeather = False
	weather = []
	location = getLoc()
	temp = ""
	humidity = ""
	pressure = ""
	if location != 0:
		doWeather = True
		weatherurl = f"https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/{location}"

	while True:
		now = datetime.datetime.now()
		today_date = now.strftime("%d %m %yyyy")
		today_time = now.strftime("%H:%M:%S")
		today_minute = now.strftime("%M")
		today_second = int( now.strftime("%S"))

		if (last_weather_check <= datetime.datetime.now() - datetime.timedelta(minutes=20)): doWeather = True

		if today_time != today_last_time:
			today_last_time = today_time

			now = datetime.datetime.now()
			today_date = now.strftime("%d %b %y")

			if today_minute != today_last_minute:
				today_last_minute = today_minute
				if cx > 10:
					cx = 5
				else:
					cx += 1


			cy = min(device.height, 128) / 2

			textArray.append(today_time)
			textArray.append(today_date)
			if doWeather:
				feed = feedparser.parse(weatherurl)

				response = requests.get(weatherurl)
				response.raise_for_status()
				feed = feedparser.parse(response.content)
				entry = feed.entries[0]
				msg = entry.title
				print(msg)
				tempArray = msg.split(",")
				weather = tempArray[0].split(":")[1].strip().split(" ")

				print(weather)
				last_weather_check = datetime.datetime.now()
				doWeather = False

			textArray.append("")
			if sensor.get_sensor_data():
				if today_second % 5 == 0:
					display_mode = modes.pop(0)
					modes.append(display_mode)

				if display_mode == "TEMPERATURE":
					textArray.append("TEMPERATURE")
					#if (temp == ""):
					temp = get_temperature()
					textArray.append(temp)
				elif display_mode == "HUMIDITY":
					textArray.append("HUMIDITY")
					#if (humidity == ""):
					humidity = get_humidity()
					textArray.append(humidity)
				elif display_mode == "ADVANCED":
					temp = ""
					humidity = ""
					pressure = ""

					if location == 0:
						textArray.append("Spearfish")
						textArray.append("TIMEKEEPER")
					else:
						for weatherItem in weather:
							textArray.append(weatherItem)
				else:
					textArray.append("PRESSURE")
					#if (pressure == ""):
					pressure = get_pressure()
					textArray.append(pressure)



			draw_text(cx, 16)
			textArray.clear()

		time.sleep(0.1)

def draw_text(cx, spacing):
	current_y = 5
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
	with canvas(device) as draw:
		for element in textArray:
			draw.text((cx, current_y), element, fill="white", font=font)
			current_y += spacing


def get_temperature():
	return str(sensor.data.temperature) + "°C"


def get_humidity():
	return str(sensor.data.humidity) + "%"

def get_pressure():
	return str(sensor.data.pressure) + "hPa"

if __name__ == "__main__":
	try:
		device = get_device()
		try:
			sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
		except (RuntimeError, IOError):
			sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

		sensor.set_humidity_oversample(bme680.OS_2X)
		sensor.set_pressure_oversample(bme680.OS_4X)
		sensor.set_temperature_oversample(bme680.OS_8X)
		sensor.set_filter(bme680.FILTER_SIZE_3)

		main()
	except KeyboardInterrupt:
		pass