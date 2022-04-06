from pathlib import Path
import serial.tools.list_ports

def find_ximc_serial_devices():
	"""Find all the XIMC devices connected via USB to your computer.
	
	Returns
	-------
	ximc_devices_found: list
		A list of the form:
		```
		[
			{'manufacturer': 'XIMC', 'description': str, 'port': str, 'serial_number': str}, # Device 1
			{'manufacturer': 'XIMC', 'description': str, 'port': str, 'serial_number': str}, # Device 2
			...
		]
		```
	"""
	return [{'manufacturer': p.manufacturer, 'description': p.description, 'port': p.device, 'serial_number': p.serial_number} for p in serial.tools.list_ports.comports() if 'XIMC' == p.manufacturer]

def map_coordinates_to_serial_ports(stages_coordinates: dict):
	"""Returns a dictionary with the mapping of which coordinate is connected
	to each serial port.
	
	Arguments
	---------
	stages_connections: dict
		A dictionary mapping each stage serial number to a coordinate, e.g.
		```
		stages_coordinates = {
			'00003A57': 'x',
			'00003A48': 'y',
			'000038CE': 'z',
		}
		```
		This is a function of how you connect each motor to each controller.
		If you don't know how to find the ID of each controller, have 
		a look at the script `list_usb_serial_ports.sh` which should be
		in the same directory as this file.
	
	Returns
	-------
	coordinates_mapping_to_ports: dict
		A dictionary of the form
		```
		{'x': '/dev/ttyACM2', 'y': '/dev/ttyACM3', 'z': '/dev/ttyACM1'}
		```
	"""
	coordinates_mapping_to_ports = {}
	for device in find_ximc_serial_devices():
		coordinates_mapping_to_ports[stages_coordinates[device['serial_number']]] = device['port']
	if any([not coord in coordinates_mapping_to_ports for coord in {'x','y','z'}]):
		raise RuntimeError(f'Cannot find the connections of the stages.')
	return coordinates_mapping_to_ports
