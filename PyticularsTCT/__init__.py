from .stage import TCTStages
from .ParticularsLaserControl import ParticularsLaserControl

class ParticularsTCT:
	def __init__(self, x_stage_port='COM3', y_stage_port='COM4', z_stage_port='COM5', laser_frequency=50):
		self.stages = TCTStages(x_stage_port, y_stage_port, z_stage_port)
		self.laser = ParticularsLaserControl(frequency=laser_frequency)
