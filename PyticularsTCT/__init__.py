from .stage import TCTStages
from .ParticularsLaserController import ParticularsLaserController
import platform
	
class TCT:
	"""Just a container for both the stages and the laser."""
	def __init__(self, x_stage_port, y_stage_port, z_stage_port):
		self.stages = TCTStages(x_stage_port, y_stage_port, z_stage_port)
		self.laser = ParticularsLaserController()
