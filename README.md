# PyticularsTCT

Package to control [Particulars TCT](http://particulars.si/) in Python.

## Installation

```
pip3 install git+https://github.com/SengerM/PyticularsTCT
```

## Usage

This was only tested in the PC located in the G floor lab under Windows and in Python 3. It works fine.

```Python
import PyticularsTCT as PTCT

x_stage = PTCT.Stage(port = 'COM3') # Use NiMax to find the port of each stage.
y_stage = PTCT.Stage(port = 'COM4')
z_stage = PTCT.Stage(port = 'COM5')

print('Starging position = ' + str(z_stage.position)) # Prints the current position in meters.
z_stage.move_to(0) # Move the stage to the 0 position.
print(z_stage.position)
z_stage.move_to(1e-2) # Moves the stage 1 cm in forward direction.
print(z_stage.position)
z_stage.move_rel(-1e-3) # Move the stage 1 mm in backward direction.
print(z_stage.position)
z_stage.move_rel(21e-3) # Moves the stage 2.1 cm in forward direction.
print(z_stage.position)
```

## More info

### About the stages

The X,Y,Z stages in the setup are controlled by [8SMC5-USB - Stepper & DC Motor Controller](http://www.standa.lt/products/catalog/motorised_positioners?item=525). The programming interface is descripted [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming.html). In the "comunity examples" section of the previous link I found [this repository](https://github.com/Negrebetskiy/Attenuator) which I took as stargint point to write PyticularsTCT.
