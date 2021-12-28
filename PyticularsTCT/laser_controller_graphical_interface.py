import tkinter as tk
import tkinter.messagebox
import tkinter.font as tkFont
import threading
import time
from .ParticularsLaserController import ParticularsLaserController

class graphical_ParticularsLaserStatusDisplay(tk.Frame):
	def __init__(self, parent, laser: ParticularsLaserController, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self._auto_update_interval = 1 # seconds
		
		if not isinstance(laser, ParticularsLaserController):
			raise TypeError(f'`laser` must be an instance of {repr(ParticularsLaserController)}, received object of type {type(laser)}.')
		self._laser = laser
		
		frame = tk.Frame(self)
		frame.grid(pady=5)
		tk.Label(frame, text = 'Laser is').grid()
		self.status_label = tk.Label(frame, text = '?')
		self.status_label.grid()
		
		frame = tk.Frame(self)
		frame.grid(pady=5)
		tk.Label(frame, text = 'DAC').grid()
		self.DAC_label = tk.Label(frame, text = '?')
		self.DAC_label.grid()
		
		frame = tk.Frame(self)
		frame.grid(pady=5)
		tk.Label(frame, text = 'Frequency').grid()
		self.frequency_label = tk.Label(frame, text = '?')
		self.frequency_label.grid()
		
		self.automatic_display_update('on')
		
	def update_display(self):
		self.status_label.config(text=f'{repr(self._laser.status)}')
		self.DAC_label.config(text=f'{self._laser.DAC}')
		self.frequency_label.config(text=f'{int(self._laser.frequency)} Hz')
	
	def automatic_display_update(self, status):
		if not isinstance(status, str):
			raise TypeError(f'<status> must be a string, received {status} of type {type(status)}.')
		if status.lower() not in {'on','off'}:
			raise ValueError(f'<status> must be either "on" or "off", received {status}.')
		self._automatic_display_update_status = status
		
		def thread_function():
			while self._automatic_display_update_status == 'on':
				try:
					self.update_display()
				except:
					pass
				time.sleep(.6)
		
		self._automatic_display_update_thread = threading.Thread(target = thread_function)
		self._automatic_display_update_thread.start()
	
	def terminate(self):
		self.automatic_display_update('off')
	
class graphical_ParticularsLaserControlInput(tk.Frame):
	def __init__(self, parent, laser, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		if not isinstance(laser, ParticularsLaserController):
			raise TypeError(f'`laser` must be an instance of {repr(ParticularsLaserController)}, received object of type {type(laser)}.')
		self._laser = laser
		
		entries_frame = tk.Frame(self)
		entries_frame.grid(
			pady = 2
		)
		
		inputs_frame = tk.Frame(entries_frame)
		inputs_frame.grid()
		
		tk.Label(inputs_frame, text = f'DAC ').grid(
			row = 0,
			column = 0,
			pady = 2,
		)
		self.DAC_entry = tk.Entry(inputs_frame, validate = 'key')
		self.DAC_entry.grid(
			row = 0,
			column = 1,
			pady = 2,
		)
		for key in {'<Return>','<KP_Enter>'}:
			self.DAC_entry.bind(key, self.update_DAC)
		
		tk.Label(inputs_frame, text = f'Frequency ').grid(
			row = 1,
			column = 0,
			pady = 2,
		)
		self.frequency_entry = tk.Entry(inputs_frame, validate = 'key')
		self.frequency_entry.grid(
			row = 1,
			column = 1,
			pady = 2,
		)
		for key in {'<Return>','<KP_Enter>'}:
			self.frequency_entry.bind(key, self.update_frequency)
		
		self.status_button = tk.Button(entries_frame, text='Turn on' if self._laser.status=='off' else 'Turn off', command=self._status_button_clicked)
		self.status_button.grid(
			pady = 22,
		)
		
	def _status_button_clicked(self):
		if self._laser.status == 'on':
			self._laser.off()
		elif self._laser.status == 'off':
			self._laser.on()
		self.status_button.config(text='Turn on' if self._laser.status=='off' else 'Turn off')
	
	def update_DAC(self, event=None):
		try:
			DAC_to_set = int(self.DAC_entry.get())
		except ValueError:
			tk.messagebox.showerror(message = f'Check your input. DAC must be an integer number, received {repr(self.DAC_entry.get())}.')
			return
		try:
			self._laser.DAC = DAC_to_set
		except Exception as e:
			tk.messagebox.showerror(message = f'Cannot update DAC. Reason: {repr(e)}.')
	
	def update_frequency(self, event=None):
		try:
			frequency_to_set = float(self.frequency_entry.get())
		except ValueError:
			tk.messagebox.showerror(message = f'Check your input. Frequency must be a float number, received {repr(self.frequency_entry.get())}.')
			return
		try:
			self._laser.frequency = frequency_to_set
		except Exception as e:
			tk.messagebox.showerror(message = f'Cannot update frequency. Reason: {repr(e)}.')

class LaserControllerGraphicalInterface_main(tk.Frame):
	def __init__(self, parent, laser, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		
		if not isinstance(laser, ParticularsLaserController):
			raise TypeError(f'`laser` must be an instance of {repr(ParticularsLaserController)}, received object of type {type(laser)}.')
		self._laser = laser
		
		main_frame = tk.Frame(self)
		main_frame.grid(padx=5,pady=5)
		display = graphical_ParticularsLaserStatusDisplay(main_frame, laser)
		display.grid(pady=5)
		graphical_ParticularsLaserControlInput(main_frame, laser).grid(pady=0)
		
		self._display = display
	
	def terminate(self):
		self._display.terminate()

if __name__ == '__main__':
	laser = ParticularsLaserController()

	root = tk.Tk()
	default_font = tkFont.nametofont("TkDefaultFont")
	default_font.configure(size=16)
	root.title('Pyticulars laser control')
	main_frame = tk.Frame(root)
	main_frame.grid(padx=20,pady=20)
	tk.Label(main_frame, text = 'Pyticulars laser control', font=("Georgia", 22, "bold")).grid()
	main_frame.grid()
	laser_controller = LaserControllerGraphicalInterface_main(main_frame, laser)
	laser_controller.grid()
	def on_closing():
		laser_controller.terminate()
		root.destroy()
	root.protocol("WM_DELETE_WINDOW", on_closing)

	root.mainloop()
