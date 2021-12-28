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

###########################################################


TEMPORARY_FILES_PATH = Path(__file__).parent.resolve()

def m2steps(m: float):
	# Converts "meters" to "steps".
	return math.floor(m*1e6/2.5), int((m*1e6/2.5-math.floor(m*1e6/2.5))*2**8)

def steps2m(steps, usteps):
	# Converts "steps" to "meters".
	return steps*2.5*1e-6 + usteps*2.5*1e-6/2**8

def default_stages_ports():
	# The following default ports I found in the computers at our lab, don't know if they default to that in any computer.
	if platform.system() == 'Windows':
		X_STAGE_DEFAULT_PORT = 'COM5'
		Y_STAGE_DEFAULT_PORT = 'COM4'
		Z_STAGE_DEFAULT_PORT = 'COM3'
	elif platform.system() == 'Linux':
		X_STAGE_DEFAULT_PORT = '/dev/ttyACM2'
		Y_STAGE_DEFAULT_PORT = '/dev/ttyACM1'
		Z_STAGE_DEFAULT_PORT = '/dev/ttyACM0'
	else:
		X_STAGE_DEFAULT_PORT = None
		Y_STAGE_DEFAULT_PORT = None
		Z_STAGE_DEFAULT_PORT = None
	return {'x': X_STAGE_DEFAULT_PORT, 'y': Y_STAGE_DEFAULT_PORT, 'z': Z_STAGE_DEFAULT_PORT}

class Stage:
	"""
	https://libximc.xisupport.com/doc-en/index.html
	"""
	def __init__(self, port: str):
		if not isinstance(port, str):
			raise TypeError('<port> must be a string (e.g. "COM3" in Windows or "/dev/ttyACM2" in Linux)')
		def create_uri(port):
			if platform.system() == 'Windows':
				return b'xi-com:\\\\.\\'+(bytes(port, 'utf8'))
			elif platform.system() in {'Linux','Darwin'}:
				return b'xi-com:'+(bytes(port, 'utf8'))
		self._dev_id = pyximc.lib.open_device(create_uri(port)) # https://libximc.xisupport.com/doc-en/ximc_8h.html#a9027dc684f63de34956488bffe9e4b36
		
		temporary_file_to_indicate_that_this_stage_is_busy = TEMPORARY_FILES_PATH/Path(f'__stage_{port.replace("/","_")}_is_busy__')
		if temporary_file_to_indicate_that_this_stage_is_busy.is_file():
			raise RuntimeError(f'Cannot open stage in port {port} because it is already in use. If it is not in use, please manually delete the file {temporary_file_to_indicate_that_this_stage_is_busy}')
		with open(temporary_file_to_indicate_that_this_stage_is_busy, 'w') as tempfile:
			print('delete me', file=tempfile)
		atexit.register(lambda: temporary_file_to_indicate_that_this_stage_is_busy.unlink()) # Delete the temporary file when this instance is destroyed.
		
	def __del__(self):
		pyximc.lib.close_device(ctypes.byref(ctypes.c_int(self._dev_id)))
	
	def reset_position(self):
		"""Resets the coordinates. This makes the stage to travel to the end, it does some stuff, and then it goes back to the middle where the 0 position is defined. This is useful because sometimes, for some reason, the stages change their coordinate origin. Dont ask me why..."""
		pyximc.lib.command_homezero(self._dev_id)
	
	def _move_to(self, steps: int, usteps: int, blocking: bool):
		# ~ Moves the stage to absolute position given by <steps> and <usteps>. If <blocking> is True, the execution of the program is blocked until the stage reaches the new position.
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
		# ~ Moves the stage relative position given by <steps> and <usteps>. If <blocking> is True, the execution of the program is blocked until the stage reaches the new position.
		if not isinstance(steps, int):
			raise TypeError('<steps> must be an int')
		if not isinstance(usteps, int):
			raise TypeError('<usteps> must be an int')
		if not 0 <= usteps <= 255:
			raise ValueError('<usteps> must be between 0 and 255 (1 step = 255 usteps)')
		pyximc.lib.command_movr(self._dev_id, steps, usteps)
		if blocking == True:
			pyximc.lib.command_wait_for_stop(self._dev_id, 10)
	
	def move_to(self, m, blocking=True):
		# Move to <m> position, where <m> is in meters.
		# If <blocking> is True, the execution of the program is blocked until the moving operation is completed, else the execution of the program continues while the stage is moving.
		if not (isinstance(m, float) or isinstance(m, int)):
			raise ValueError(f'Position must be a float number, received object of type {type(m)}.')
		steps, usteps = m2steps(m)
		self._move_to(steps, usteps, blocking = blocking)
	
	def move_rel(self, m, blocking=True):
		# Move relative <m> meters.
		# If <blocking> is True, the execution of the program is blocked until the moving operation is completed, else the execution of the program continues while the stage is moving.
		if not (isinstance(m, float) or isinstance(m, int)):
			raise ValueError(f'Position must be a float number, received object of type {type(m)}.')
		steps, usteps = m2steps(m)
		if steps == usteps == 0:
			warnings.warn(f'I was told to move the stage in <m>={m} meters (relative to its current position) and this is less than the minimum step of the stage, thus it will not be moved.')
		self._move_rel(steps, usteps, blocking = blocking)
	
	def get_position(self):
		# Returns the position of the stage in "steps", "usteps" and "EncPosition" I don't know what it means.
		pos = pyximc.get_position_t()
		pyximc.lib.get_position(self._dev_id, ctypes.byref(pos))
		return {'Position': pos.Position, 'uPosition': pos.uPosition, 'EncPosition': pos.EncPosition}
	
	@property
	def serial_number(self):
		serial_number = ctypes.c_uint(100)
		pyximc.lib.get_serial_number(self._dev_id, ctypes.byref(serial_number))
		return serial_number.value
	
	@property
	def information(self):
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
		# Returns the position of the stage in meters. E.g. "my_stage.position".
		pos = self.get_position()
		return steps2m(pos['Position'], pos['uPosition'])

class TCTStages:
	def __init__(self, x_stage_port, y_stage_port, z_stage_port, x_limits=[-50e-3, 50e-3], y_limits=[-50e-3, 50e-3], z_limits=[0,90e-3]):
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
	
	def move_to(self, x=None, y=None, z=None):
		"""Move the mechanical stages to an absolute position, values go in meters."""
		for stage, pos, coord in zip(self._stages, [x,y,z], ['x','y','z']):
			if pos == None:
				continue
			if not self.coordinates_limits[coord][0] < pos < self.coordinates_limits[coord][1]:
				raise ValueError(f'Coordinate {repr(coord)} must be inside the range {self.coordinates_limits[coord]}, received {pos}.')
			stage.move_to(pos,blocking=True)
	
	def move_rel(self, x=None, y=None, z=None):
		"""Move the mechanical stages relative to the current position, values in meters."""
		movement_vector = [None]*3
		for i, xyz in enumerate([x,y,z]):
			movement_vector[i] = 0 if xyz is None else xyz
		self.move_to(*list(np.array(self.position)+np.array(movement_vector)))
	
	@property
	def position(self):
		"""Return the current position of the stages in meters as a tuple of the form (x,y,z)."""
		return tuple([stage.position for stage in self._stages])
	
	def reset_position(self):
		"""Reset the position of all the stages. WARNING: This will move one by one each stage to the border and then will go to the 0 position."""
		for stage in [self.x_stage, self.y_stage, self.z_stage]:
			stage.reset_position()
