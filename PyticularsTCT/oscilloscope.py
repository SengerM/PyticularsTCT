import pyvisa

class LecroyWR640Zi:
    def __init__(self, name):
        rm = pyvisa.ResourceManager()
        self.resource = rm.open_resource(name)
    
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
        raw_data = list(self.resource.read_raw())[360:-1] # By some unknown reason the first 359 samples are crap, and also the last one.
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
        return {'t': times, 'v': volts}

    def acquire_one_pulse(self):
        current_trigger = self.query('TRIG_MODE?')
        self.write('TRIG_MODE SINGLE') # We want the 4 channels from a single trigger.
        # I assume that the triggering is almost instantaneous so I don't have to put a delay here.
        signals = {}
        for ch in [1,2,3,4]:
            signals[f'CH{ch}'] = self.get_wf(CH=ch)
        self.write('TRIG_MODE ' + current_trigger) # Set the trigger back to the original configuration.
        return signals