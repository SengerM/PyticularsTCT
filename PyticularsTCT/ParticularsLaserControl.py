from pathlib import Path
from subprocess import check_output
import platform

if not platform.system() == 'Windows':
	raise OSError('Particulars laser control software is only available for Windows, I am sorry. You can contact the manufacturers in case there is a version for your operating system.')

PaLaserEXE_path = (Path(__file__).parent/Path('laser_api/PaLaser-C_API_V1.0/PaLaser.exe')).resolve()

class ParticularsLaserControl():
	def __init__(self, frequency=50, default_DAC_value=0):
		if frequency <=0 or not isinstance(frequency, int):
			raise ValueError(f'<frequency> must be a positive integer number.')
		self.frequency = int(frequency)
		self.set_DAC(default_DAC_value)
	
	def set_DAC(self, value: int):
		"""Set the value of the so called "DAC" that controls (in an obscure and very non-linear way) the number of photons that the laser emmits in each pulse. Low values of DAC will emmit many photons while high values of DAC will produce very few photons."""
		if not 0<=value<=3300 or not isinstance(value, int):
			raise ValueError(f'<value> must be an integer number between 0 and 3300, received {repr(value)} of type {type(value)}.')
		current_status = self.status
		check_output(str(PaLaserEXE_path) + f' -p {value}')
		self._current_DAC_value = value
		self.status = current_status
	
	def on(self):
		"""Turn on the laser in "single frequency mode" using the specified frequency when creating the object."""
		check_output(str(PaLaserEXE_path) + f' -f {self.frequency}')
	
	def off(self):
		"""Turn off the laser."""
		check_output(str(PaLaserEXE_path) + ' -off')
		
	@property
	def status(self):
		"""Returns the status of the laser, i.e. "on" or "off"."""
		answer = check_output(str(PaLaserEXE_path) + ' -s').decode()
		if 'Laser in OFF!' in answer:
			return 'off'
		elif 'Laser in ON and running!' in answer:
			return 'on'
		else:
			raise RuntimeError(f'Cannot determine the status of the laser because I cannot understand the answer from the controller. The answer was:\n\n{answer}')
	@status.setter
	def status(self, status: str):
		"""Turns on or off the laser in "single frequency mode"."""
		if status in {'on', 'ON', True}:
			self.on()
		elif status in {'off', 'OFF', False}:
			self.off()
		else:
			raise ValueError(f'Dont know what to do, allowed values are "on" and "off", received {repr(status)} instead...')
	
	@property
	def DAC(self):
		"""Returns the current value of the "DAC" that controls the number of photons in each pulse."""
		return self._current_DAC_value
	@DAC.setter
	def DAC(self, value:int):
		"""Set the value of the "DAC" that controls the number of photons in each pulse."""
		self.set_DAC(value)

if __name__ == '__main__':
	# This is an usage example ---
	import time
	laser = ParticularsLaserControl()
	laser.on()
	for DAC in [0,111,555]:
		laser.DAC = int(DAC)
		print(f'DAC = {laser.DAC}')
		time.sleep(1)
	laser.off()
