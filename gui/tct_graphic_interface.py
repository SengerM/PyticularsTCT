#!/usr/bin/env python3

# Usage: Just run this script and enjoy the grahpical interface:
# ```
# python3 tct_graphic_interface.py
# ```

from laser_controller_graphical_interface import LaserControllerGraphicalInterface_main
from stages_graphical_interface import StagesControlGraphicalInterface_main
import tkinter as tk
from PyticularsTCT.ParticularsLaserController import ParticularsLaserController
from PyticularsTCT.stage import TCTStages
import tkinter.font as tkFont
from PyticularsTCT.find_ximc_stages import map_coordinates_to_serial_ports

root = tk.Tk()
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=16)
root.title('Pyticulars TCT control')
main_frame = tk.Frame(root)
main_frame.grid(padx=20,pady=20)
main_frame.grid()
tk.Label(main_frame, text = 'Pyticulars TCT setup control', font=("Georgia", 22, "bold")).grid(pady=10)
widgets_frame = tk.Frame(main_frame)
widgets_frame.grid()

stages_coordinates = { # This is what I have in the lab, in your case it may be different. (Matias, 23.March.2022)
	'XIMC_XIMC_Motor_Controller_00003A48': 'x',
	'XIMC_XIMC_Motor_Controller_00003A57': 'y',
	'XIMC_XIMC_Motor_Controller_000038CE': 'z',
}
ports_dict = map_coordinates_to_serial_ports(stages_coordinates)

stages_widget = StagesControlGraphicalInterface_main(
	widgets_frame, 
	stages = TCTStages(x_stage_port=ports_dict['x'], y_stage_port=ports_dict['y'], z_stage_port=ports_dict['z']),
)
stages_widget.grid(
	row = 0,
	column = 0,
	sticky = 'n',
)
laser_controller_widget = LaserControllerGraphicalInterface_main(
	widgets_frame, 
	laser = ParticularsLaserController()
)
laser_controller_widget.grid(
	row = 0,
	column = 1,
	padx = (99,0),
	sticky = 'n',
)

def on_closing():
	laser_controller_widget.terminate()
	root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
