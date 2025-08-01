# -*- coding: utf-8 -*-
# Copyright (c) 2014-2022 Richard Hull and contributors
'''
MIT License
===========

Copyright (c) 2017-2023 Richard Hull and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import sys
import logging
from wsgiref.util import request_uri

from luma.core import cmdline, error

locations = []

# logging
logging.basicConfig(
	level=logging.DEBUG,
	format='%(asctime)-15s - %(message)s'
)
# ignore PIL debug messages
logging.getLogger('PIL').setLevel(logging.ERROR)

def getLoc():
	return locations[0] if len(locations) > 0 else "0"

def display_settings(device, args):
	"""
	Display a short summary of the settings.

	:rtype: str
	"""
	iface = ''
	display_types = cmdline.get_display_types()
	if args.display not in display_types['emulator']:
		iface = f'Interface: {args.interface}\n'

	lib_name = cmdline.get_library_for_display_type(args.display)
	if lib_name is not None:
		lib_version = cmdline.get_library_version(lib_name)
	else:
		lib_name = lib_version = 'unknown'

	import luma.core
	version = f'luma.{lib_name} {lib_version} (luma.core {luma.core.__version__})'

	return f'Version: {version}\nDisplay: {args.display}\n{iface}Dimensions: {device.width} x {device.height}\n{"-" * 60}'


def get_device(actual_args=None):
	"""
	Create device from command-line arguments and return it.
	"""
	if actual_args is None:
		actual_args = sys.argv[1:]
	parser = cmdline.create_parser(description='luma.examples arguments')
	parser.add_argument('--location', type=str, help='Specify a BBC Weather location')

	args = parser.parse_args(actual_args)

	if args.location:
		locations.append(int(args.location))

	if args.config:
		# load config from file
		config = cmdline.load_config(args.config)
		args = parser.parse_args(config + actual_args)

	# create device
	try:
		device = cmdline.create_device(args)
		print(display_settings(device, args))
		return device

	except error.Error as e:
		parser.error(e)
		return None