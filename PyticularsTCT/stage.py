import os
import sys
import time
import ctypes
import math

if sys.version_info >= (3,0):
	import urllib.parse

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)

if sys.platform in ("win32", "win64"):
	libdir = os.path.join(ximc_dir, sys.platform)
	os.environ["Path"] = libdir + ";" + os.environ["Path"]

import pyximc

###########################################################

def m2steps(m: float):
	# Converts "meters" to "steps".
	return math.floor(m*1e6/2.5), int((m*1e6/2.5-math.floor(m*1e6/2.5))*2**8)

def steps2m(steps, usteps):
	# Converts "steps" to "meters".
	return steps*2.5*1e-6 + usteps*2.5*1e-6/2**8

class Stage:
	"""
	https://libximc.xisupport.com/doc-en/index.html
	"""
	def __init__(self, port: str):
		if not isinstance(port, str):
			raise TypeError('<port> must be a string (e.g. "COM3")')
		self._dev_id = pyximc.lib.open_device(b'xi-com:\\\\.\\'+(bytes(port, 'utf8'))) # https://libximc.xisupport.com/doc-en/ximc_8h.html#a9027dc684f63de34956488bffe9e4b36
	
	def __del__(self):
		pyximc.lib.close_device(ctypes.byref(ctypes.c_int(self._dev_id)))
	
	def reset_position(self):
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
		steps, usteps = m2steps(m)
		self._move_to(steps, usteps, blocking = blocking)
	
	def move_rel(self, m, blocking=True):
		# Move relative <m> meters.
		# If <blocking> is True, the execution of the program is blocked until the moving operation is completed, else the execution of the program continues while the stage is moving.
		steps, usteps = m2steps(m)
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
	
