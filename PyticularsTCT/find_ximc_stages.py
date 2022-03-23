import platform
import subprocess
from pathlib import Path

def find_ximc_usb_devices():
	"""Find all the XIMC devices connected via USB to your computer.
	
	Returns
	-------
	ximc_devices_found: list
		A list of the form:
		```
		{'ID_SERIAL': 'XIMC_XIMC_Motor_Controller_00003A57', 'Path': '/dev/ttyACM2'}
		{'ID_SERIAL': 'XIMC_XIMC_Motor_Controller_00003A48', 'Path': '/dev/ttyACM3'}
		{'ID_SERIAL': 'XIMC_XIMC_Motor_Controller_000038CE', 'Path': '/dev/ttyACM1'}
		```
	"""
	SEPARATOR = ' bio675DFtivTVCRxe5UCW ' # This comes from the `list_usb_serial_ports.sh` script. It is just something with low probability of occurrence.
	SCRIPT_THAT_LISTS_THE_USB_DEVICES_PATH = Path(__file__).parent/Path("list_usb_serial_ports.sh")
	
	if platform.system() != 'Linux':
		raise NotImplementedError(f'This function was only implemented for Linux.')
	
	bash_script_output = subprocess.run([f'bash {SCRIPT_THAT_LISTS_THE_USB_DEVICES_PATH}'], stdout=subprocess.PIPE, shell=True).stdout.decode()
	ximc_devices_found = []
	for s in bash_script_output.split('\n'):
		if 'XIMC_XIMC_Motor_Controller' in s:
			this_controller_data = {}
			for ss in s.split(SEPARATOR):
				this_controller_data[ss.split('::: ')[0]] = ss.split('::: ')[1]
			ximc_devices_found.append(this_controller_data)
	return ximc_devices_found

def map_coordinates_to_serial_ports(stages_coordinates: dict):
	"""Returns a dictionary with the mapping of which coordinate is connected
	to each serial port.
	
	Arguments
	---------
	stages_connections: dict
		A dictionary mapping each stage to a coordinate, e.g.
		```
		stages_coordinates = {
			'XIMC_XIMC_Motor_Controller_00003A57': 'x',
			'XIMC_XIMC_Motor_Controller_00003A48': 'y',
			'XIMC_XIMC_Motor_Controller_000038CE': 'z',
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
	if platform.system() == 'Linux':
		for device in find_ximc_usb_devices():
			coordinates_mapping_to_ports[stages_coordinates[device['ID_SERIAL']]] = device['Path']
	else:
		raise NotImplementedError('Cannot find default ports in your operating system.')
	if any([not coord in coordinates_mapping_to_ports for coord in {'x','y','z'}]):
		raise RuntimeError(f'Cannot find the connections of the stages.')
	return coordinates_mapping_to_ports
