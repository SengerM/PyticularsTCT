# PyticularsTCT

Package to control [Particulars TCT](http://particulars.si/) easily from Python.

## Installation

```
pip3 install git+https://github.com/SengerM/PyticularsTCT
```

This package was developed and tested only in our setup at UZH.

## Usage

Usage example:

**`WARNING`** This example is outdated as I am going through a major update to make this cross platform.

```Python
import PyticularsTCT
import time
import numpy as np

tct = PyticularsTCT.ParticularsTCT() # Note: PYYYYYYticularsTCT.PAAAAAArticularsTCT()

# Sweep laser intensity ---
tct.laser.on()
for DAC in np.linspace(0,1666,5):
	tct.laser.DAC = int(DAC) # Change the intensity of the laser.
	print(f'Laser DAC = {tct.laser.DAC}')
	time.sleep(1)

# Sweep position ---
current_position = tct.stages.position # Store current position to go back in the end.
for x in current_position[0] + np.linspace(-55e-6,55e-6,11):
	tct.stages.move_to(x=x)
	print(f'Current position is {tct.stages.position}')
	time.sleep(1)
tct.stages.move_to(*current_position) # Go back to original position.
```

## More info

### About the stages

The X,Y,Z stages in the setup are controlled by [8SMC5-USB - Stepper & DC Motor Controller](http://www.standa.lt/products/catalog/motorised_positioners?item=525). The programming interface is descripted [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming.html). In the "comunity examples" section of the previous link I found [this repository](https://github.com/Negrebetskiy/Attenuator) which I took as stargint point to write PyticularsTCT.

In [this link](https://libximc.xisupport.com/doc-en/index.html) there is documentation about *libximc*.

### About the laser

I was able to implement a pure-Python driver for the laser, you can find it [here](PyticularsTCT/ParticularsLaserControl.py). Being pure-Python it should be cross platform (I have only tested it on Linux by now). If you want to use this module individually, here there is an example:
```
from PyticularsTCT.ParticularsLaserController import ParticularsLaserController
from time import sleep

laser = ParticularsLaserController() # Open connection to laser.
laser.on() # This is equivalent to `laser.status = 'on'`.
print(f'Current laser status is: {laser.status}') # This should print "on".
for frequency in [50,100,1e3,10e3,100e3]:
	for DAC in [0,222,444,666,888,1023]:
		print(f'Setting f = {frequency} Hz, DAC = {DAC}...')
		laser.frequency = frequency # Change the frequency.
		laser.DAC = DAC # Change the DAC, from 0 to 1023.
		print(f'Current frequency = {laser.frequency} Hz') # This prints the current frequency.
		print(f'Current DAC = {laser.DAC}') # This prints the current DAC value.
		sleep(.5)
print('Will turn the laser off...')
laser.off() # This is equivalent to `laser.status = 'off'`.
print(f'Laser status is: {laser.status}')
```
