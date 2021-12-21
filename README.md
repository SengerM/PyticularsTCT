# PyticularsTCT

Package to control [Particulars TCT](http://particulars.si/) easily from Python.

## Installation

### Installation instructions for Linux

The following line
```
pip3 install git+https://github.com/SengerM/PyticularsTCT
```
should be enough.

After installing [PyUSB](https://github.com/pyusb/pyusb) you may get the common permission error `USBError: [Errno 13] Access denied (insufficient permissions)`. [This](https://stackoverflow.com/questions/50625363/usberror-errno-13-access-denied-insufficient-permissions/70436368#70436368) solved the problem for me.

### Installation instructions for Windows

1. First clone (or download) this repo in your favourite directory.
2. Run
```
pip3 install -e C:\wherever\you\cloned\this\repo
```
3. Install the file `vcredist_x64.exe` located in [`PyticularsTCT/PyticularsTCT/ximc/win64`](PyticularsTCT/ximc/win64). (You already downloaded it, just navigate within the repo to that file.)

Now it should work.

### Further installation instructions

This package depends on others which you will have to install (you will discover when you first try to use this one). Most of them are easy but some, such as [PyUSB](https://github.com/pyusb/pyusb), may be more tricky. However you should be able to make it work with help from Google.

This package was developed and tested only in our setup at UZH. It worked both on Linux (Ubuntu 20.04) and Windows (10).

## Usage

Usage example:
```Python
import PyticularsTCT
import time
import numpy as np

tct = PyticularsTCT.TCT()

# Sweep laser intensity ---
tct.laser.on()
for DAC in np.linspace(0,1023,5):
	tct.laser.DAC = int(DAC) # Change the intensity of the laser.
	print(f'Laser DAC = {tct.laser.DAC}')
	time.sleep(1)

# Sweep position using the mechanical stages ---
current_position = tct.stages.position # Store current position to go back in the end.
print(f'Start position: {current_position}')
tct.laser.DAC = 0 # This is the most intense setting.
for z in current_position[2] + np.linspace(-555e-6,555e-6,11):
	tct.stages.move_to(z=z) # Values here go in meters.
	print(f'Current position is {tct.stages.position}')
	time.sleep(1)
tct.stages.move_to(*current_position) # Go back to original position.
```
Ideally you should use the `TCT` class defined in the [`__init__.py`](PyticularsTCT/__init__.py) file that abstracts the whole setup. This is a very simple class which has a `stages` artribute containing an instance of `TCTStages` defined in [`stage.py`](PyticularsTCT/stage.py) and an instance of `ParticularsLaserController` defined in [`ParticularsLaserController.py`](PyticularsTCT/ParticularsLaserController.py). The documentation is in the docstrings.

## More info

### About the motorized stages

The X,Y,Z stages in the setup are controlled by [8SMC5-USB - Stepper & DC Motor Controller](http://www.standa.lt/products/catalog/motorised_positioners?item=525) units. The programming interface is descripted [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming.html). *PyticularsTCT* is shipped with a hardcoded copy of the binaries for some operating systems together with a slightly modified version of the Python script that is provided by the original author of the *ximc library* (see [`PyticularsTCT/ximc`](PyticularsTCT/ximc)) in such a way that the control of the motors becomes easier. More information in the [`README.md`](PyticularsTCT/ximc/README.md) file located in [`PyticularsTCT/ximc`](PyticularsTCT/ximc).

If you want control only the motors as a standalone package here there is an example:
```Python
from PyticularsTCT.stage import TCTStages

stages = TCTStages(
	z_stage_port = '/dev/ttyACM0', # To know what to write here, if you are in Linux https://unix.stackexchange.com/a/144735/317682, in Windows it is 'COM1' and so.
	x_stage_port = '/dev/ttyACM1', 
	y_stage_port = '/dev/ttyACM2',
)

print(stages.position) # Print (x,y,z) position.
stages.move_rel(z = 1e-2) # Move z in 1 centimiter.
print(stages.position)
stages.move_rel(z = -1e-2) # Move z in -1 centimiter.
print(stages.position) # Position should be the initial position.
stages.move_rel(x = 1e-6, y = 1e-6) # Move 1 µm both in x and y.
current_position = stages.position
stages.move_to(0,0,0) # Move to x=y=z=0.
print(stages.position)
stages.move_to(*current_position) # Go back to previous position.
```
If, for some very weird reason, you want to control each of the motorized stages individually it is also possible, have a look at [the source code of `stage.py`](PyticularsTCT/stage.py).

### About the laser

The [PyticularsLaserController](PyticularsTCT/ParticularsLaserController.py) is a pure Python module. If you want to use this module individually, here there is an example:
```Python
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
