# Usage: Just run this script and enjoy the grahpical interface:
# ```
# python3 tct_graphic_interface.py
# ```

from PyticularsTCT.laser_controller_graphical_interface import LaserControllerGraphicalInterface_main
from PyticularsTCT.stages_graphical_interface import StagesControlGraphicalInterface_main
import tkinter as tk
from PyticularsTCT.ParticularsLaserController import ParticularsLaserController
from PyticularsTCT.stage import TCTStages, default_stages_ports
import tkinter.font as tkFont

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
stages_widget = StagesControlGraphicalInterface_main(
	widgets_frame, 
	stages = TCTStages(x_stage_port=default_stages_ports().get('x'), y_stage_port=default_stages_ports().get('y'), z_stage_port=default_stages_ports().get('z')),
)
stages_widget.grid(
	row = 0,
	column = 0,
)
laser_controller_widget = LaserControllerGraphicalInterface_main(
	widgets_frame, 
	laser = ParticularsLaserController()
)
laser_controller_widget.grid(
	row = 0,
	column = 1,
	padx = (99,0),
)

def on_closing():
	laser_controller_widget.terminate()
	root.destroy()
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
