import sys
import time
import ctypes
import math
import warnings
from pathlib import Path
import atexit
import numpy as np
import platform

if sys.version_info >= (3,0):
	import urllib.parse

pyximc_path = Path(__file__).parent/Path('ximc')
sys.path.append(str(pyximc_path))

import pyximc

TEMPORARY_FILES_PATH = (Path.home()/Path('.PyticularsTCT')).resolve()
TEMPORARY_FILES_PATH.mkdir(parents=True, exist_ok=True)

def m2steps(m: float):
	# Converts "meters" to "steps".
	return math.floor(m*1e6/2.5), int((m*1e6/2.5-math.floor(m*1e6/2.5))*2**8)

def steps2m(steps, usteps):
	# Converts "steps" to "meters".
	return steps*2.5*1e-6 + usteps*2.5*1e-6/2**8

class Stage:
	"""A class to control the stages that are used in the TCT setup."""
	# https://libximc.xisupport.com/doc-en/index.html
	def __init__(self, port: str):
		"""Create an instance of `Stage`.
		
		Parameters
		----------
		port: str
			A string with the port name. If you are in Linux it will look
			something like `"dev/ttyACM2"`, if you are in Windows it should
			be something like `"COM2"`. 
		"""
		if not isinstance(port, str):
			raise TypeError(f'`port` must be a string but received object of type {type(port)}.')
		def create_uri(port):
			if platform.system() == 'Windows':
				return b'xi-com:\\\\.\\'+(bytes(port, 'utf8'))
			elif platform.system() in {'Linux','Darwin'}:
				return b'xi-com:'+(bytes(port, 'utf8'))
		self._dev_id = pyximc.lib.open_device(create_uri(port)) # https://libximc.xisupport.com/doc-en/ximc_8h.html#a9027dc684f63de34956488bffe9e4b36
		
		temporary_file_to_indicate_that_this_stage_is_busy = TEMPORARY_FILES_PATH/Path(f'Pyticulars__stage_{port.replace("/","_")}_is_busy__')
		if temporary_file_to_indicate_that_this_stage_is_busy.is_file():
			raise RuntimeError(f'Cannot open stage in port {repr(port)} because it seems to be already in use. If it is not in use, please manually delete the file {repr(temporary_file_to_indicate_that_this_stage_is_busy)}')
		with open(temporary_file_to_indicate_that_this_stage_is_busy, 'w') as tempfile:
			print('delete me', file=tempfile)
		atexit.register(lambda: temporary_file_to_indicate_that_this_stage_is_busy.unlink()) # Delete the temporary file when this instance is destroyed.
		
	def __del__(self):
		pyximc.lib.close_device(ctypes.byref(ctypes.c_int(self._dev_id)))
	
	def reset_position(self):
		"""Resets the coordinates. This makes the stage to travel to the 
		end, it does some stuff, and then it goes back to the middle 
		where the 0 position is defined.
		"""
		pyximc.lib.command_homezero(self._dev_id)
	
	def _move_to(self, steps: int, usteps: int, blocking: bool):
		"""Moves the stage to the absolute position defined in `steps` and
		`usteps`.
		
		Parameters
		----------
		steps: int
			Value of `steps` for the position you want to go to.
		usteps: int
			Value of `usteps` (micro steps) for the position you want 
			to go to.
		blocking: bool
			If `True`, the execution of the program is blocked until the
			stage reaches the final position.
		"""
		if not isinstance(steps, int):
			raise TypeError('<steps> must be an int')
		if not isinstance(usteps, int):
			raise TypeError('<usteps> must be an int')
		if not 0 <= usteps <= 255:
			raise ValueError('<usteps> must be between 0 and 255 (1 step = 255 usteps)')
		pyximc.lib.command_move(self._dev_id, steps, usteps) # https://libximc.xisupport.com/doc-en/ximc_8h.html#aa6113a42efa241396c72226bba9acd59
		if blocking == True:
			pyximc.lib.command_wait_for_stop(self._dev_id, 10) # https://libximc.xisupport.com/doc-en/ximc_8h.html#ad9324f278bf9b97ad85b3411562ef0f7
	
	def _move_rel(self, steps: int, usteps: int, blocking: bool):
		"""Moves the stage relative to the current position.
		
		Parameters
		----------
		steps: int
			Number of steps to move the stage.
		usteps: int
			Number of micro steps to move the stage.
		blocking: bool
			If `True`, the execution of the program is blocked until the
			stage reaches the final position.
		"""
		if not isinstance(steps, int):
			raise TypeError('<steps> must be an int')
		if not isinstance(usteps, int):
			raise TypeError('<usteps> must be an int')
		if not 0 <= usteps <= 255: # Not sure if this can be negative...
			raise ValueError('<usteps> must be between 0 and 255 (1 step = 255 usteps)')
		pyximc.lib.command_movr(self._dev_id, steps, usteps)
		if blocking == True:
			pyximc.lib.command_wait_for_stop(self._dev_id, 10)
	
	def move_to(self, m: float, blocking: bool=True):
		"""Move the stage to some absolute position defined in meters.
		
		Parameters
		----------
		m: float
			Value of the position to go to, in meters.
		blocking: bool, default True
			If `True`, the execution of the program is blocked until the
			stage reaches the final position.
		"""
		if not (isinstance(m, float) or isinstance(m, int)):
			raise ValueError(f'Position must be a float number, received object of type {type(m)}.')
		steps, usteps = m2steps(m)
		self._move_to(steps, usteps, blocking = blocking)
	
	def move_rel(self, m, blocking=True):
		"""Move the stage relative to the current position, in meters.
		
		Parameters
		----------
		m: float
			Value of the distance to move, in meters.
		blocking: bool, default True
			If `True`, the execution of the program is blocked until the
			stage reaches the final position.
		"""
		if not (isinstance(m, float) or isinstance(m, int)):
			raise ValueError(f'Position must be a float number, received object of type {type(m)}.')
		steps, usteps = m2steps(m)
		if steps == usteps == 0:
			warnings.warn(f'I was told to move the stage in <m>={m} meters (relative to its current position) and this is less than the minimum step of the stage, thus it will not be moved.')
		self._move_rel(steps, usteps, blocking = blocking)
	
	def get_position(self):
		"""Returns the position of the stage. Returns a dictionary of 
		the form
		```
		{'Position': int, 'uPosition': int, 'EncPosition': ?}
		```
		where `'Position'` is measured in steps and `'uPosition'` is
		measured in micro-steps. I don't know what `'EncPosition'` has,
		never used it.
		"""
		pos = pyximc.get_position_t()
		pyximc.lib.get_position(self._dev_id, ctypes.byref(pos))
		return {'Position': pos.Position, 'uPosition': pos.uPosition, 'EncPosition': pos.EncPosition}
	
	@property
	def serial_number(self):
		"""Returns the serial number of the stage."""
		serial_number = ctypes.c_uint(100)
		pyximc.lib.get_serial_number(self._dev_id, ctypes.byref(serial_number))
		return serial_number.value
	
	@property
	def information(self):
		"""Returns a dictionary with general information about the stage
		such as manufacturer name, firmware version, etc."""
		info = pyximc.device_information_t()
		pyximc.lib.get_device_information(self._dev_id, ctypes.byref(info))
		return {
			"Manufacturer": info.Manufacturer.decode("utf-8"),
			"ManufacturerId": info.ManufacturerId.decode("utf-8"),
			"ProductDescription": info.ProductDescription.decode("utf-8"),
			"Major": info.Major,
			"Minor": info.Minor,
			"Release": info.Release,
		}
	
	@property
	def position(self):
		"""Returns the position of the stage in meters as a float number.
		"""
		pos = self.get_position()
		return steps2m(pos['Position'], pos['uPosition'])

class TCTStages:
	"""A class to wrap the three xyz stages of the TCT setup."""
	def __init__(self, x_stage_port, y_stage_port, z_stage_port, x_limits=[-50e-3, 50e-3], y_limits=[-50e-3, 50e-3], z_limits=[0,90e-3]):
		"""Creates an instance of the class.
		
		Parameters:
		x_, y_, z_stage_port: str
			String with the name of the port to which each stage is 
			connected, e.g. `x_stage_port = "dev/ttyACM2"' in Linux.
		x_, y_, z_limits: list of the form [float, float]
			Constrain the value of each coordinate to move within these
			boundaries. This is useful to avoid moving the stage to a
			position like `50` instead of `50e-3` that will make it go to
			the end and loose the 0 coordinate.
			Default values are
			```
			x_limits=[-50e-3, 50e-3]
			y_limits=[-50e-3, 50e-3]
			z_limits=[0,90e-3]
			```
		"""
		# The default values for the limits were found after using the "Stage.reset_position" method. With these numbers there should be no problems.
		self.x_stage = Stage(port=x_stage_port)
		self.y_stage = Stage(port=y_stage_port)
		self.z_stage = Stage(port=z_stage_port)
		self._stages = [self.x_stage, self.y_stage, self.z_stage]
		self.coordinates_limits = {
			'x': x_limits,
			'y': y_limits,
			'z': z_limits,
		}
	
	def move_to(self, x: float=None, y: float=None, z:float =None):
		"""Move the stages to an absolute position. `x`, `y` and `z` are
		in meters.
		"""
		for stage, pos, coord in zip(self._stages, [x,y,z], ['x','y','z']):
			if pos == None:
				continue
			if not self.coordinates_limits[coord][0] <= pos <= self.coordinates_limits[coord][1]:
				raise ValueError(f'Coordinate {repr(coord)} must be inside the range {self.coordinates_limits[coord]}, received {pos}.')
			stage.move_to(pos,blocking=True)
	
	def move_rel(self, x=None, y=None, z=None):
		"""Move the stages relative to the current position. `x`, `y` and
		`z` are in meters.
		"""
		movement_vector = [None]*3
		for i, xyz in enumerate([x,y,z]):
			movement_vector[i] = 0 if xyz is None else xyz
		self.move_to(*list(np.array(self.position)+np.array(movement_vector)))
	
	@property
	def position(self):
		"""Return the current position of the stages in meters as a 
		tuple of the form (x,y,z).
		"""
		return tuple([stage.position for stage in self._stages])
	
	def reset_position(self):
		"""Reset the position of all the stages. 
		
		WARNING
		-------
		This will move one by one each stage to the border and 
		then will go to the 0 position. So be sure that there is space
		for the stages to move!!
		"""
		for stage in [self.x_stage, self.y_stage, self.z_stage]:
			stage.reset_position()
