# PyticularsTCT

Package to control [Particulars TCT](http://particulars.si/) easily from Python.

## Installation

```
pip3 install git+https://github.com/SengerM/PyticularsTCT
```

This package was developed and tested only in our setup at UZH.

## Usage

Usage example:

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

The software to control the laser, which is propietary of Particulars I think, is only available for Windows. It was sent to me via email, but later I found it in [the Particulars website](http://particulars.si/support.php?sup=downloads.html), specifically clicking in "Microsoft Visual C++". Anyway, I included a copy in this repo so it is plug and play.
