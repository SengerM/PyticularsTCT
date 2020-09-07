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
        raw_data = list(self.resource.read_raw())
        volt = []
        for sample in raw_data:
            if sample > 127:
                sample -= 255
            volt.append(sample)
        for sample in volt:
            sample = sample/25*float(self.query('c1:vdiv?')) - float(self.query('c1:ofst?'))
        return volt[360:-1] # By some unknown reason the first 359 samples are crap, and also the last one.
    
    def acquire_one_pulse(self):
        current_trigger = self.query('TRIG_MODE?')
        self.write('TRIG_MODE SINGLE') # We want the 4 channels from a single trigger.
        # I assume that the triggering is almost instantaneous so I don't have to put a delay here.
        signals = {}
        for ch in [1,2,3,4]:
            signals[f'CH{ch}'] = self.get_wf(CH=ch)
        self.write('TRIG_MODE ' + current_trigger) # Set the trigger back to the original configuration.
        return signals

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    osc = LecroyWR640Zi('USB0::0x05FF::0x1023::2810N60091::INSTR')
    print('IDN: ' + osc.idn)
    print('Acquiring signals...')
    signals = osc.acquire_one_pulse()
    print('Plotting...')
    fig, ax = plt.subplots()
    for ch in list(signals.keys()):
        ax.plot(signals[ch], label = ch, marker = '.')
    ax.legend()
    plt.show()