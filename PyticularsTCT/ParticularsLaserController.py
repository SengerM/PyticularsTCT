import usb.core
import usb.util
from time import sleep
from warnings import warn
import platform

def int_to_char_cpp_style(i: int):
	if not isinstance(i, int):
		raise TypeError(f'`i` must be an int.')
	return int(f'{i:b}'[-8:], 2)

class ParticularsLaserController:
	"""This class allows to control the laser from the Particulars TCT setup. It is based in the C++ source code `USBM3.cxx` that Particulars sent to me after request to use the laser from Linux. I did not implemented every feature, only what I need."""
	def __init__(self):
		device = usb.core.find(idVendor=0xC251, idProduct=0x2201) # ID c251:2201 Keil Software, Inc. LASER Driver IJS
		if device is None:
			raise RuntimeError(f'Cannot find the laser controller within the USB devices. Be sure it is connected and that it is recognized by the computer.')
		if platform.system() == 'Linux':
			interface = device[0].interfaces()[0]
			if device.is_kernel_driver_active(interface.bInterfaceNumber): # Not sure why this is needed, but fails without it.
				device.detach_kernel_driver(interface.bInterfaceNumber)
		
		self.device = device
		self.endpoint = device[0].interfaces()[0].endpoints()[0]
		
		self._frequency = 1e3 # Initialize.
		self._DAC = 0 # Initialize.
		current_status = self.status
		self._turn_on() # This updates the real frequency and DAC.
		if current_status == 'off':
			self._turn_off()
	
	@property
	def frequency(self):
		"""Return the current value for the frequency."""
		return getattr(self, '_frequency', None)
	@frequency.setter
	def frequency(self, Hz: float):
		"""Set the frequency in Hz."""
		try:
			Hz = float(Hz)
		except:
			raise TypeError(f'`Hz` must be a number, received object of type {type(Hz)}.')
		if hasattr(Hz, '__iter__'): # This is to prevent numpy arrays that will pass the previous check.
			raise TypeError(f'`Hz` must be a number, received object of type {type(Hz)}.')
		if not 50 <= Hz <= 100e3:
			raise ValueError(f'`Hz` must be within 50 and 100e3, received {Hz} Hz.')
		self._frequency = Hz
		if self.status == 'on':
			self._turn_on() # This is to force an update of the frequency.
	
	@property
	def DAC(self):
		"""Return the current value for the DAC."""
		return getattr(self, '_DAC', None)
	@DAC.setter
	def DAC(self, DAC: int):
		"""Set the DAC value."""
		if not isinstance(DAC, int):
			raise TypeError(f'`DAC` must be an integer number.')
		if not 0 <= DAC < 1024:
			raise ValueError(f'`DAC` must be in [0,1024).')
		self._DAC = DAC
		if self.status == 'on':
			self._turn_on() # This is to force an update on the DAC.
	
	@property
	def status(self):
		"""Returns either 'on' or 'off'."""
		# Tutorial for reading from USB: https://www.youtube.com/watch?v=xfhzbw93rzw
		for k in [1,2]: # Read twice because otherwise it tends to fail in the first one, don't ask me why...
			data = self.endpoint.read(size_or_buffer = 64) # This number comes from the C++ code. It is also the `wMaxPacketSize`. 
		STATUS_BIT = 6 # This I took from the C++ code.
		if data[STATUS_BIT] == 1:
			return 'on'
		elif data[STATUS_BIT] == 0:
			return 'off'
		else:
			raise RuntimeError('Cannot understand response from laser controller, dont know if the laser is on or off.')
	@status.setter
	def status(self, status: str):
		"""Set the laser 'on' or 'off'."""
		if status not in {'on','off'}:
			raise ValueError(f'`status` must be either "on" or "off", received {repr(status)}.')
		if status == 'on':
			self.on()
		else:
			self.off()
	
	def on(self):
		"""Turn the laser on."""
		if self.status == 'off':
			self._turn_on()
	
	def off(self):
		"""Turn the laser off."""
		if self.status == 'on':
			self._turn_off()
	
	def _send_packet(self, packet):
		"""Send a packet of bytes from the computer to the laser controller. I converged into this function after spending a lot of time reading from here and from there. I left below some references that were useful to me:
			- https://stackoverflow.com/questions/37943825/send-hid-report-with-pyusb/52368526#52368526
			- https://stackoverflow.com/a/52368526/8849755
			- https://github.com/pyusb/pyusb/blob/629943a1d73aeb912222c7dc6eaaea0d64a94a08/usb/core.py#L1043
		`packet` is an array of bytes, i.e. an array of integer numbers each in 0, 1, ..., 255. Example `packet = [0,4,200]`.
		"""
		if not hasattr(packet, '__iter__') or not all([isinstance(byte, int) for byte in packet]) or any([not 0<=byte<=2**8 for byte in packet]):
			raise ValueError(f'`packet` must be an array of integers each between 0 and 255. Received {repr(packet)}.')
		if platform.system() == 'Windows':
			packet = packet + (64-len(packet))*[0]
		number_of_bytes_sent = self.device.ctrl_transfer(
			bmRequestType = 0x21, # I have no idea why this number...
			bRequest = 9, # I have no idea why this number...
			wValue = 0x200, # I have no idea why this number...
			wIndex = 0, # I have no idea why this number...
			data_or_wLength = packet,
		)
		if number_of_bytes_sent != len(packet):
			warn(f'I tried to send {len(packet)} bytes but only {number_of_bytes_sent} were sent...')
		sleep(.01) # A small sleep to avoid issues if many commands are sent one after the other.
		return number_of_bytes_sent
	
	def _turn_on(self):
		"""Turn on the laser at the configured frequency and DAC values."""
		self._set_frequency(Hz = self.frequency)
		self._set_DAC(DAC = self.DAC)
		self._hardware_sequence_enable()
	
	def _turn_off(self):
		"""Turn the laser off."""
		self._send_packet([90])
		self._send_packet([4])
	
	def _set_frequency(self, Hz: float):
		"""Set the frequency of the laser."""
		if not 50 <= Hz <= 100e3:
			raise ValueError(f'`Hz` must be within 50 and 100e3, received {Hz} Hz.')
		Hz = int((500000000/Hz - 440)/180) # Taken from the C++ code.
		cmd = [99, int_to_char_cpp_style(Hz), int_to_char_cpp_style(Hz>>8)] # Taken from the C++ code.
		self._send_packet(cmd)
	
	def _hardware_sequence_enable(self):
		"""Turn the laser on?"""
		self._send_packet([91]) # Taken from the C++ code.

	def _enable_DAC(self):
		self._send_packet([92]) # Taken from the C++ code.

	def _disable_DAC(self):
		self._send_packet([93]) # Taken from the C++ code.

	def _set_DAC(self, DAC: int):
		if not isinstance(DAC, int):
			raise TypeError(f'`DAC` must be an integer number, received {repr(DAC)}.')
		if not 0 <= DAC < 1024:
			raise ValueError(f'`DAC` must be in [0,1024).')
		self._turn_off()
		self._enable_DAC()
		self._send_packet([94, int_to_char_cpp_style(DAC), int_to_char_cpp_style(DAC>>8)]) # Taken from the C++ code.
		self._hardware_sequence_enable()

if __name__ == '__main__':
	# This is an usage example.
	laser = ParticularsLaserController()
	laser.on() # Will turn on with the default frequency and DAC.
	for dac in [0,111,222,333,444,555]:
		print(f'Setting DAC = {dac}...')
		laser.DAC = dac
		sleep(1)
	laser.frequency = 1e3 # Set the frequency to 1 kHz.
	laser.off()
