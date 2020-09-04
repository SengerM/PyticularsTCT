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

print('Starging position = ' + str(z_stage.get_position()))
z_stage.move_to(0) # Move the stage to the 0 position.
print(z_stage.get_position())
z_stage.move_to(
    steps = 999,
    usteps = 100,
) # Move the stage to the 999 steps and 100 microsteps position. (I believe that 1 step = 256 µsteps = 2.5 µm.)
print(z_stage.get_position())
z_stage.move_rel(1) # Move the stage 10 steps forward
print(z_stage.get_position())
z_stage.move_rel(-10) # Move the stage 10 steps backwards
print(z_stage.get_position())
```

## More info

### About the stages

The X,Y,Z stages in the setup are controlled by [8SMC5-USB - Stepper & DC Motor Controller](http://www.standa.lt/products/catalog/motorised_positioners?item=525). The programming interface is descripted [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming.html). In the "comunity examples" section of the previous link I found [this repository](https://github.com/Negrebetskiy/Attenuator) which I took as stargint point to write PyticularsTCT.
