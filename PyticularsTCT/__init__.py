from .stage import TCTStages, default_stages_ports
from .ParticularsLaserController import ParticularsLaserController
import platform
	
class TCT:
	def __init__(self, x_stage_port=default_stages_ports().get('x'), y_stage_port=default_stages_ports().get('y'), z_stage_port=default_stages_ports().get('z')):
		self.stages = TCTStages(x_stage_port, y_stage_port, z_stage_port)
		self.laser = ParticularsLaserController()
