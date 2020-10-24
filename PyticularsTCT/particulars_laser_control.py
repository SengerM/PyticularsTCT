import pyautogui
import clipboard
pyautogui.FAILSAFE = False

LASER_ON_OFF_BTN_POS = (54,413)
PULSE_WIDTH_TAB_POS = (211,48)
SINGLE_FREQUENCY_TAB_POS = (38,41)
SET_LASER_PULSE_WIDTH_TXT_POS = (108,175)
SET_LASER_PULSE_WIDTH_INCREASE_BTN_POS = (134,172)
SET_LASER_PULSE_WIDTH_DECREASE_BTN_POS = (134,185)
SET_LASER_PULSE_WIDTH_SET_NEW_VALUE_BTN_POS = (214,178)

def turn_laser_off():
	pyautogui.click(*PULSE_WIDTH_TAB_POS)
	pyautogui.click(*SINGLE_FREQUENCY_TAB_POS)

def turn_laser_on():
	turn_laser_off()
	pyautogui.click(*SINGLE_FREQUENCY_TAB_POS)
	pyautogui.click(*LASER_ON_OFF_BTN_POS)

def set_pulse_width(percentage: float):
	percentage = float(percentage)
	if not 0<=percentage<=100:
		raise ValueError(f'<percentage> must be between 0 and 100, received {percentage}')
	percentage = f'{percentage:.1f}'.replace('.',',')
	pyautogui.click(*PULSE_WIDTH_TAB_POS)
	pyautogui.click(*SET_LASER_PULSE_WIDTH_TXT_POS)
	pyautogui.click(*SET_LASER_PULSE_WIDTH_TXT_POS)
	pyautogui.typewrite(percentage)
	pyautogui.click(*SET_LASER_PULSE_WIDTH_SET_NEW_VALUE_BTN_POS)

def get_pulse_width():
	pyautogui.click(*PULSE_WIDTH_TAB_POS)
	pyautogui.click(*SET_LASER_PULSE_WIDTH_TXT_POS)
	pyautogui.click(*SET_LASER_PULSE_WIDTH_TXT_POS)
	pyautogui.hotkey('ctrl','c')
	return float(clipboard.paste().replace(',','.'))

class ParticularsLaserControl():
	def __init__(self):
		input('This is "ParticularsLaserControl", please position the window in the upper left corner and leave it uncovered so I can control the mouse and act on it.')
		self.status = 'off' # Start with the laser off so I can track the status
	
	def __del__(self):
		self.status = 'off' # Turn the laser off in the end
	
	@property
	def pulse_width(self):
		current_status = self.status
		width = get_pulse_width()
		self.status = current_status
		return width
	@pulse_width.setter
	def pulse_width(self, val: float):
		current_status = self.status
		set_pulse_width(val)
		self.status = current_status
	
	@property
	def status(self):
		return self._status
	@status.setter
	def status(self, val: str):
		if not isinstance(val, str):
			raise TypeError(f'Must specify a string either "on" or "off", received {val} of type {type(val)}')
		if val.lower() not in ['on', 'off']:
			raise ValueError(f'Must be either "on" or "off", received "{val}"')
		if val == 'on':
			turn_laser_on()
			self._status = 'on'
		elif val == 'off':
			turn_laser_off()
			self._status = 'off'

if __name__ == '__main__':
	from  time import sleep
	laser = ParticularsLaserControl()
	laser.status = 'on'
	laser.pulse_width = 79
	print(f'Laser is {laser.status} at {laser.pulse_width} % of pulse width')
