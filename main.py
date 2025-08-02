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
	display_mode = "TEMPERATURE"
	last_weather_check = datetime.datetime.now() - datetime.timedelta(hours=2)
	cx = 5
	modes = ["ADVANCED", "TEMPERATURE", "HUMIDITY", "PRESSURE"]
	doWeather = False
	weather = []
	location = getLoc()
	ctemp = ""
	humidity = ""
	pressure = ""
	if location != 0:
		doWeather = True
		weatherurl = f"https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/{location}"

	while True:
		with open("/sys/class/thermal/thermal_zone0/temp") as temp_file:
			cpu_temp = float(temp_file.read()) / 1000.0
			while cpu_temp > 50:
				textArray.append("WARNING")
				textArray.append("CPU TEMP")
				textArray.append(get_cpu_temperature())
				draw_text(cx, 18)
				textArray.clear()
				time.sleep(2)


		now = datetime.datetime.now()
		today_date = now.strftime("%d %m %Y")
		today_time = now.strftime("%H:%M:%S")
		today_minute = now.strftime("%M")
		current_hour = int(now.strftime("%H"))
		today_second = int( now.strftime("%S"))
		if (current_hour < 9) or (current_hour > 21):
			time.sleep(20)
			continue
		if (last_weather_check <= datetime.datetime.now() - datetime.timedelta(minutes=20)): doWeather = True

		if today_time != today_last_time:
			today_last_time = today_time

			now = datetime.datetime.now()
			today_date = now.strftime("%d %b %y")

			if today_minute != today_last_minute:
				today_last_minute = today_minute
				if cx > 10:
					cx = 2
				else:
					cx += 1


			cy = min(device.height, 128) / 2

			textArray.append(today_time)
			textArray.append(today_date)
			if doWeather:
				try:
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
				except:
					weather.clear()
					weather.append("ERROR")
					weather.append("FETCHING")
					weather.append("WEATHER")

			textArray.append("")
			if sensor.get_sensor_data():
				if today_second % 5 == 0:
					display_mode = modes.pop(0)
					modes.append(display_mode)

				if display_mode == "TEMPERATURE":
					textArray.append("TEMPERATURE")
					if (ctemp == ""):
						ctemp = get_cpu_temperature()

					textArray.append(get_temperature())
					textArray.append(ctemp)
				elif display_mode == "HUMIDITY":
					textArray.append("HUMIDITY")
					#if (humidity == ""):
					humidity = get_humidity()
					textArray.append(humidity)
					if (sensor.data.humidity > 65):
						textArray.append("[!] TOO HIGH")
					elif (sensor.data.humidity < 35):
						textArray.append("[!] TOO LOW")
					else:
						textArray.append("[i] NORMAL")
				elif display_mode == "ADVANCED":
					ctemp = ""
					humidity = ""
					pressure = ""

					if location == 0:
						textArray.append("Spearfish")
						textArray.append("TIMEKEEPER")
						textArray.append(" advanced ")
					else:
						for weatherItem in weather:
							textArray.append(weatherItem)
				else:
					textArray.append("PRESSURE")
					#if (pressure == ""):
					pressure = get_pressure()
					textArray.append(pressure)



			draw_text(cx, 18)
			textArray.clear()

		time.sleep(0.1)

def draw_text(cx, spacing):
	current_y = 5
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 18)
	with canvas(device) as draw:
		for element in textArray:
			if (datetime.datetime.now().second % 2 == 0):
				draw.text((cx, current_y), element, fill="white", font=font)
			else:
				draw.text((cx, current_y), element, fill="white", font=font)
			current_y += spacing



def get_temperature():
	return str(sensor.data.temperature) + "°C"

def get_cpu_temperature():
	with open("/sys/class/thermal/thermal_zone0/temp") as temp_file:
		cpu_temp = float(temp_file.read()) / 1000.0
		return "CPU: " + str(round(cpu_temp, 1)) + "°C"

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