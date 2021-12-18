import sys
import time
import ctypes
import math
import warnings
from pathlib import Path
import atexit
import numpy as np

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

if __name__ == '__main__':
	# This is a simple graphical interface to control the stages ---
	
	import tkinter as tk
	import tkinter.messagebox
	import numpy as np
	import numbers

	class CoordinatesFrame(tk.Frame):
		def __init__(self, parent, coordinates_name=None, *args, **kwargs):
			tk.Frame.__init__(self, parent, *args, **kwargs)
			self.parent = parent
			
			if coordinates_name != None:
				tk.Label(self, text = f'{coordinates_name}:').grid()
			self.entries_coordinates = {}
			entries_frame = tk.Frame(self)
			entries_frame.grid()
			for idx,coord in enumerate(['x', 'y', 'z']):
				tk.Label(entries_frame, text = f'{coord} (mm) = ').grid(
					row = idx,
					column = 0,
					pady = 2,
				)
				self.entries_coordinates[coord] = tk.Entry(entries_frame, validate = 'key')
				self.entries_coordinates[coord].grid(
					row = idx,
					column = 1,
					pady = 2,
				)
				self.entries_coordinates[coord].insert(0,'?')
				
		def get_coordinates(self):
			coords = []
			for coord in ['x', 'y', 'z']: 
				try:
					coords.append(float(self.entries_coordinates[coord].get())*1e-3)
				except ValueError:
					coords.append(self.entries_coordinates[coord].get())
			return tuple(coords)
		
		def set_coordinates(self, x=None, y=None, z=None):
			for xyz,coord in zip([x,y,z],['x', 'y', 'z']):
				if xyz == None:
					continue
				if not isinstance(xyz, numbers.Number):
					raise TypeError(f'Coordinates must be numbers, received {xyz} of type {type(xyz)}')
				self.entries_coordinates[coord].delete(0,'end')
				self.entries_coordinates[coord].insert(0,xyz*1e3)

	class CoordinatesControl(tk.Frame):
		def __init__(self, parent, stages, coordinates_name=None, *args, **kwargs):
			tk.Frame.__init__(self, parent, *args, **kwargs)
			self.parent = parent
			
			self.stages = stages
			
			self.coordinates = CoordinatesFrame(parent=self,coordinates_name=coordinates_name)
			self.coordinates.grid()
			
			self.jump_to_position_btn = tk.Button(self,text = 'Go to this position', command = self.jump_to_position_btn_command)
			self.jump_to_position_btn.grid()
			
		def jump_to_position_btn_command(self):
			position_to_go_to = self.coordinates.get_coordinates()
			for val in position_to_go_to:
				try:
					float(val)
				except:
					tk.messagebox.showerror(message = f'Check your input. Coordinates must be float numbers, received "{val}"')
					return
			print(f'Moving stages to {position_to_go_to}...')
			self.stages.move_to(*position_to_go_to)
			new_pos = self.stages.position
			print(f'Stages moved, new position is {new_pos}')
			self.coordinates.set_coordinates(*new_pos)
		
		def get_coordinates(self):
			return self.coordinates.get_coordinates()
		
		def set_coordinates(self, x=None, y=None, z=None):
			self.coordinates.set_coordinates(x,y,z)

	class CoordinatesMemory(tk.Frame):
		def __init__(self, parent, stages, coordinates_name=None, *args, **kwargs):
			tk.Frame.__init__(self, parent, *args, **kwargs)
			self.parent = parent
			
			self.stages = stages
			self.coordinates_control = CoordinatesControl(self, stages, coordinates_name=coordinates_name)
			self.coordinates_control.grid()
			self.store_position_btn = tk.Button(self, text = 'Store current position', command = self.store_current_position_command)
			self.store_position_btn.grid()
		
		def store_current_position_command(self):
			current_pos = stages.position
			self.coordinates_control.set_coordinates(*current_pos)
			print(f'Stored current position...')
		
		def get_coordinates(self):
			return self.coordinates_control.get_coordinates()
		
		def set_coordinates(self, x=None, y=None, z=None):
			self.coordinates_control.set_coordinates(x,y,z)
			

	class StagesJoystick(tk.Frame):
		def __init__(self, parent, stages, current_coordinates_display, *args, **kwargs):
			tk.Frame.__init__(self, parent, *args, **kwargs)
			self.parent = parent
			
			self.stages = stages
			self.current_coordinates_display = current_coordinates_display
			
			step_frame = tk.Frame(self)
			controls_frame = tk.Frame(self)
			step_frame.grid()
			controls_frame.grid()
			xy_frame = tk.Frame(controls_frame)
			z_frame = tk.Frame(controls_frame)
			xy_frame.grid(row=0,column=0)
			z_frame.grid(row=0,column=1)
			tk.Label(step_frame, text='xy step (µm) = ').grid(row=0,column=0)
			tk.Label(step_frame, text='z step (µm) = ').grid(row=1,column=0)
			
			self.xy_step_entry = tk.Entry(step_frame)
			self.xy_step_entry.grid(row=0,column=1)
			self.xy_step_entry.insert(0,'1')
			self.xy_step_entry.bind('<Left>', lambda x: self.move_command('x','-'))
			self.xy_step_entry.bind('<Right>', lambda x: self.move_command('x','+'))
			self.xy_step_entry.bind('<Up>', lambda x: self.move_command('y','+'))
			self.xy_step_entry.bind('<Down>', lambda x: self.move_command('y','-'))
			self.xy_step_entry.bind('<Control_R>', lambda x: self.move_command('z','-'))
			self.xy_step_entry.bind('<Shift_R>', lambda x: self.move_command('z','+'))
			
			self.z_step_entry = tk.Entry(step_frame)
			self.z_step_entry.grid(row=1,column=1)
			self.z_step_entry.insert(0,'100')
			self.z_step_entry.bind('<Left>', lambda x: self.move_command('x','-'))
			self.z_step_entry.bind('<Right>', lambda x: self.move_command('x','+'))
			self.z_step_entry.bind('<Up>', lambda x: self.move_command('y','+'))
			self.z_step_entry.bind('<Down>', lambda x: self.move_command('y','-'))
			self.z_step_entry.bind('<Control_R>', lambda x: self.move_command('z','-'))
			self.z_step_entry.bind('<Shift_R>', lambda x: self.move_command('z','+'))
			
			self.buttons = {}
			for xyz in ['x', 'y', 'z']:
				self.buttons[xyz] = {}
				for direction in ['-','+']:
					self.buttons[xyz][direction] = tk.Button(
						xy_frame if xyz in ['x','y'] else z_frame,
						text = f'{direction}{xyz}',
					)
					self.buttons[xyz][direction]['command'] = lambda xyz=xyz,direction=direction: self.move_command(xyz,direction)
			self.buttons['x']['-'].grid(row=1,column=0)
			self.buttons['x']['+'].grid(row=1,column=2)
			self.buttons['y']['+'].grid(row=0,column=1)
			self.buttons['y']['-'].grid(row=2,column=1)
			self.buttons['z']['-'].grid(row=0)
			self.buttons['z']['+'].grid(row=1)
		
		def move_command(self, coordinate, direction):
			try:
				step = float(self.xy_step_entry.get())*1e-6 if coordinate in ['x','y'] else float(self.z_step_entry.get())*1e-6
			except:
				tk.messagebox.showerror(message = f'Check your input in "step". It must be a float but you have entered "{self.step_entry.get()}"')
				return
			print(f'Moving {step*1e6} µm in {direction}{coordinate}...')
			move = [0,0,0]
			for idx,xyz in enumerate(['x', 'y', 'z']):
				if xyz == coordinate:
					move[idx] = step
					if direction == '-':
						move[idx] *= -1
			self.stages.move_rel(*tuple(move))
			new_pos = self.stages.position
			print(f'Stages moved, new position is {new_pos}')
			self.current_coordinates_display.set_coordinates(*new_pos)
			
	stages = TCTStages()

	root = tk.Tk()
	root.title('Pyticulares stages control')
	current_position_frame = tk.Frame(root)
	controls_frame = tk.Frame(root)
	current_position_frame.grid()
	controls_frame.grid()

	current_coordinates = CoordinatesControl(current_position_frame, stages=stages, coordinates_name='Current position')
	current_coordinates.grid()
	current_coordinates.coordinates.set_coordinates(*stages.position)
	
	joystick = StagesJoystick(parent=controls_frame, stages=stages, current_coordinates_display=current_coordinates)
	joystick.grid(pady=20)
	
	for k in range(3):
		memory = CoordinatesMemory(
			parent = root, 
			stages = stages,
			coordinates_name = f'Position memory # {k+1}',
		)
		memory.grid(pady=20)
		memory.set_coordinates(*stages.position)

	root.mainloop()
