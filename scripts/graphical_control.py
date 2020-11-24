import tkinter as tk
import tkinter.messagebox
import numpy as np
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT

########################################################################

# Interfase creation:

root = tk.Tk()
root.title('Stages control')

coordinates_display_frame = tk.Frame(root)
entries_coordinates = {}
for idx,coord in enumerate(['x', 'y', 'z']):
	tk.Label(coordinates_display_frame, text = f'{coord} (mm) = ').grid(
		row = idx,
		column = 0,
		pady = 2,
	)
	entries_coordinates[coord] = tk.Entry(coordinates_display_frame)
	entries_coordinates[coord].grid(
		row = idx,
		column = 1,
		pady = 2,
	)
	entries_coordinates[coord].insert(0,'?')

controls_frame = tk.Frame(root)
step_frame = tk.Frame(controls_frame)
tk.Label(step_frame, text='Step (µm) = ').grid()
step_entry = tk.Entry(step_frame, text = '1')
step_entry.grid(row=0,column=1)
step_entry.insert(0,'10')
xy_controls_frame = tk.Frame(controls_frame)
z_controls_frame = tk.Frame(controls_frame)
single_movement_buttons = {}
for coord in ['x', 'y', 'z']:
	single_movement_buttons[coord] = {}
	for direction in ['-','+']:
		single_movement_buttons[coord][direction] = tk.Button(
			xy_controls_frame if coord in ['x','y'] else z_controls_frame,
			text = f'{direction}{coord}',
		)
single_movement_buttons['x']['-'].grid(row=1,column=0)
single_movement_buttons['x']['+'].grid(row=1,column=2)
single_movement_buttons['y']['-'].grid(row=0,column=1)
single_movement_buttons['y']['+'].grid(row=2,column=1)
single_movement_buttons['z']['-'].grid(row=0)
single_movement_buttons['z']['+'].grid(row=1)

jump_to_position_button = tk.Button(controls_frame, text = 'Jump to position')

jump_to_position_button.grid(row=0)
step_frame.grid(row=1)
xy_controls_frame.grid(row=2,column=0)
z_controls_frame.grid(row=2,column=1)
coordinates_display_frame.grid()
controls_frame.grid()

########################################################################

# Commands:

stages = TCTStages()

def get_position():
	position = stages.position
	for idx,coord in enumerate(['x','y','z']):
		entries_coordinates[coord].delete(0,'end')
		entries_coordinates[coord].insert(0,position[idx]*1e3)
	return position

def move_stages_to(x=None,y=None,z=None):
	print(f'Moving to position {(x,y,z)}')
	stages.move_to(x,y,z)
	get_position()

def jump_to_position_button_command():
	pos = []
	for coord in ['x','y','z']:
		try:
			pos.append(float(entries_coordinates[coord].get())*1e-3)
		except:
			tk.messagebox.showerror(message = f'Check your input in "{coord}". It must be a float but you have entered "{entries_coordinates[coord].get()}"')
			return
	move_stages_to(*tuple(pos))

def single_movement_button_command(coordinate, direction):
	try:
		step = float(step_entry.get())*1e-6
	except:
		tk.messagebox.showerror(message = f'Check your input in "step". It must be a float but you have entered "{step_entry.get()}"')
	print(f'Moving {step} µm in {direction}{coordinate}')
	move = [0,0,0]
	for idx,xyz in enumerate(['x','y','z']):
		if coordinate==xyz:
			move[idx] = step
			if direction == '-':
				move[idx] *= -1
	move_stages_to(*tuple(np.array(get_position())+np.array(move)))

jump_to_position_button['command'] = jump_to_position_button_command
for xyz in ['x','y','z']:
	for pm in ['-','+']:
		single_movement_buttons[xyz][pm]['command'] = lambda coord=xyz,direction=pm: single_movement_button_command(coord,direction)

get_position()
root.mainloop()
