import pyvisa
from time import sleep

class LecroyWR640Zi:
	def __init__(self, name):
		rm = pyvisa.ResourceManager()
		self.resource = rm.open_resource(name)
		self.write('CHDR OFF') # This is to receive only numerical data in the answers and not also the echo of the command and some other stuff. See p. 22 of http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf
	
	@property
	def idn(self):
		return  self.query('*IDN?')
	
	def write(self, msg):
		self.resource.write(msg)
	
	def read(self):
		return self.resource.read()
	
	def query(self, msg):
		self.write(msg)
		return self.read()
	
	def get_wf(self, CH: int):
		# Page 223: http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf
		# Page 258: http://cdn.teledynelecroy.com/files/manuals/wr2_rcm_revb.pdf
		if not isinstance(CH, int) or not 1 <= CH <= 4:
			raise ValueError('<CH> must be in {1,2,3,4}')
		self.write(f'C{CH}:WF?')
		raw_data = list(self.resource.read_raw())[361:-1] # By some unknown reason the first 360 samples are crap, and also the last one.
		tdiv = float(self.query('TDIV?'))
		sampling_rate = float(self.query(r"""VBS? 'return=app.Acquisition.Horizontal.SamplingRate'""")) # This line is a combination of http://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf and p. 1-20 http://cdn.teledynelecroy.com/files/manuals/automation_command_ref_manual_ws.pdf
		vdiv = float(self.query('c1:vdiv?'))
		ofst = float(self.query('c1:ofst?'))
		times = []
		volts = []
		for idx,sample in enumerate(raw_data):
			if sample > 127:
				sample -= 255
			volts.append(sample/25*vdiv - ofst)
			times.append(tdiv*14/2+idx/sampling_rate)
		return {'time': times, 'volt': volts}

	def acquire_one_pulse(self):
		current_trigger = self.trig_mode
		self.trig_mode = 'AUTO' # Set it to auto so if there is no signal, it records "almost 0" (noise) and not the previous trigger.
		sleep(0.1) # Wait for the oscilloscope to change the trigger mode.
		self.trig_mode = 'SINGLE' # We want the 4 channels from a single trigger.
		# I assume that the triggering is almost instantaneous so I don't have to put a delay here.
		signals = {}
		for ch in [1,2,3,4]:
			signals[f'CH{ch}'] = self.get_wf(CH=ch)
		self.trig_mod = current_trigger # Set the trigger back to the original configuration.
		return signals
	
	@property
	def trig_mode(self):
		return self.query('TRIG_MODE?').replace('\n','')
	
	@trig_mode.setter
	def trig_mode(self, mode: str):
		self.set_trig_mode(mode)
	
	def set_trig_mode(self, mode: str):
		OPTIONS = ['AUTO', 'NORM', 'STOP', 'SINGLE']
		if not isinstance(mode, str):
			raise TypeError('<mode> must be a string')
		if mode.upper() not in OPTIONS:
			raise ValueError('<mode> must be one of ' + str(OPTIONS))
		self.write('TRIG_MODE ' + mode)
	
	def set_vdiv(self, ch: int, vdiv: float):
		if ch not in [1,2,3,4]:
			raise ValueError(f'<ch> must be an integer in [1, 2, 3, 4]. Received {ch}')
		if not isinstance(vdiv, float):
			raise ValueError(f'<vdiv> must be a float in units V/div, received {vdiv}')
		self.write(f'C{ch}:VDIV {vdiv}') # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=47
	
	def get_vdiv(self, ch: int): # Getter.
		if ch not in [1,2,3,4]:
			raise ValueError(f'<ch> must be an integer in [1, 2, 3, 4]. Received {ch}')
		return float(self.query(f'C{ch}:VDIV?')) # http://cdn.teledynelecroy.com/files/manuals/tds031000-2000_programming_manual.pdf#page=47
