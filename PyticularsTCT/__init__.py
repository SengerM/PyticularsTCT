from .stage import TCTStages
from .ParticularsLaserController import ParticularsLaserController
import platform
	
# The following default ports I found in the computers at our lab, don't know if they default to that in any computer.
if platform.system() == 'Windows':
	X_STAGE_DEFAULT_PORT = 'COM3'
	Y_STAGE_DEFAULT_PORT = 'COM4'
	Z_STAGE_DEFAULT_PORT = 'COM5'
elif platform.system() == 'Linux':
	X_STAGE_DEFAULT_PORT = '/dev/ttyACM1'
	Y_STAGE_DEFAULT_PORT = '/dev/ttyACM2'
	Z_STAGE_DEFAULT_PORT = '/dev/ttyACM0'
else:
	X_STAGE_DEFAULT_PORT = None
	Y_STAGE_DEFAULT_PORT = None
	Z_STAGE_DEFAULT_PORT = None

class TCT:
	def __init__(self, x_stage_port=X_STAGE_DEFAULT_PORT, y_stage_port=Y_STAGE_DEFAULT_PORT, z_stage_port=Z_STAGE_DEFAULT_PORT):
		self.stages = TCTStages(x_stage_port, y_stage_port, z_stage_port)
		self.laser = ParticularsLaserController()
