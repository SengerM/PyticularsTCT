# PyticularsTCT

Package to control [Particulars TCT](http://particulars.si/) using Python.

## Installation

```
pip3 install git+https://github.com/SengerM/PyticularsTCT
```
If you receive some error like ```ERROR: Could not install packages due to an EnvironmentError: [Errno 30] Read-only file system: BLA BLA BLA``` you can try instead 
```
pip3 install git+https://github.com/SengerM/PyticularsTCT --user
```
which has proven to work in the past. This solution was found [here](https://stackoverflow.com/a/53916143/8849755).

## Usage

This was only tested in the PC located in the G floor lab under Windows and in Python 3. It works fine.

```Python
from PyticularsTCT.oscilloscope import LecroyWR640Zi
from PyticularsTCT.stage import Stage
from PyticularsTCT.utils import save_4ch_trigger
import matplotlib.pyplot as plt
import numpy as np

############################################################

DELTA_X = 10e-6
N_STEPS_X = 5

############################################################

osc = LecroyWR640Zi('USB0::0x05FF::0x1023::2810N60091::INSTR')
x_stage = Stage(port='COM3')
y_stage = Stage(port='COM4')
z_stage = Stage(port='COM5')

initial_x = x_stage.position # Store it to return after measuring.
print(f'Initial position = {initial_x} m')

for nx in range(N_STEPS_X):
    print(f'Moving to position {initial_x+nx*DELTA_X} m...')
    x_stage.move_rel(nx*DELTA_X)
    print('Acquiring signals...')
    signals = osc.acquire_one_pulse()
    
    save_4ch_trigger(
        fname = f'data/{nx}.txt',
        position = (x_stage.position, y_stage.position, z_stage.position),
        data = signals,
    )
    
    fig, ax = plt.subplots()
    for ch in list(signals.keys()):
        ax.plot(
            signals[ch]['time'],
            signals[ch]['volt'],
            label = ch, 
            marker = '.'
        )
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (V)')
    ax.legend()

print('Moving back to initial position...')
x_stage.move_to(initial_x)
print(f'Current position = {x_stage.position} m')
print('Finished! :)')

plt.show()
```

## More info

### About the stages

The X,Y,Z stages in the setup are controlled by [8SMC5-USB - Stepper & DC Motor Controller](http://www.standa.lt/products/catalog/motorised_positioners?item=525). The programming interface is descripted [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming.html). In the "comunity examples" section of the previous link I found [this repository](https://github.com/Negrebetskiy/Attenuator) which I took as stargint point to write PyticularsTCT.

In [this link](https://libximc.xisupport.com/doc-en/index.html) there is documentation about *libximc*.

### Connecting to the osciloscopes from Linux

It is not plug and play but it can be done. In case ```pyvisa``` is not listing the USB resources, see [here](https://stackoverflow.com/questions/66480203/pyvisa-not-listing-usb-instrument-on-linux/66480539#66480539).
