import tkinter as tk
import tkinter.messagebox
import numpy as np
import numbers
from stage import TCTStages, default_stages_ports

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

class StagesControlGraphicalInterface_main(tk.Frame):
	def __init__(self, parent, stages, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		main_frame = tk.Frame(self)
		main_frame.grid()
		current_position_frame = tk.Frame(main_frame)
		controls_frame = tk.Frame(main_frame)
		current_position_frame.grid()
		controls_frame.grid()
		
		current_coordinates = CoordinatesControl(current_position_frame, stages=stages, coordinates_name='Current position')
		current_coordinates.grid()
		current_coordinates.coordinates.set_coordinates(*stages.position)
		
		joystick = StagesJoystick(parent=controls_frame, stages=stages, current_coordinates_display=current_coordinates)
		joystick.grid(pady=20)
		
		for k in [1,2]:
			memory = CoordinatesMemory(
				parent = main_frame, 
				stages = stages,
				coordinates_name = f'Position memory #{k}',
			)
			memory.grid(pady=20)
			memory.set_coordinates(*stages.position)

if __name__ == '__main__':
	import tkinter.font as tkFont
	
	stages = TCTStages(x_stage_port=default_stages_ports().get('x'), y_stage_port=default_stages_ports().get('y'), z_stage_port=default_stages_ports().get('z'))

	root = tk.Tk()
	default_font = tkFont.nametofont("TkDefaultFont")
	root.title('Pyticulares stages control')
	main_frame = tk.Frame(root)
	main_frame.grid(padx=20,pady=20)
	main_frame.grid()
	tk.Label(main_frame, text = 'Pyticulars stages control', font=("Georgia", 22, "bold")).grid(pady=22)
	StagesControlGraphicalInterface_main(main_frame, stages).grid()
	
	root.mainloop()
