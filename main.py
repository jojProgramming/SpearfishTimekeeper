import luma.oled
import bme680
from luma.core.mixin import capabilities

"""
An analog clockface with date & time.

Ported from:
https://gist.github.com/TheRayTracer/dd12c498e3ecb9b8b47f#file-clock-py
"""

import time
import datetime
from options import get_device
from luma.core.render import canvas

textArray = []
sensor = bme680.BME680()



def main():
	today_last_time = "Unknown"
	today_last_minute = "Unknown"
	cx = 5
	while True:
		now = datetime.datetime.now()
		today_date = now.strftime("%d %b %y")
		today_time = now.strftime("%H:%M:%S")
		today_minute = now.strftime("%M")

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
			textArray.append(today_minute)
			if sensor.get_sensor_data():
				textArray.append(get_temperature())
				textArray.append(get_humidity())
				textArray.append(get_pressure())
			draw_text(cx, 16)
			textArray.clear()

		time.sleep(0.1)

def draw_text(cx, spacing):
	current_y = 5
	with canvas(device) as draw:
		for element in textArray:
			draw.text((cx, current_y), element, fill="white")
			current_y += spacing


def get_temperature():
	return "TEMPERATURE: " + str(sensor.data.temperature)

def get_humidity():
	return "HUMIDITY: " + str(sensor.data.humidity)

def get_pressure():
	return "PRESSURE: " + str(sensor.data.temperature)

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