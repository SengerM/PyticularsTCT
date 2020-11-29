from .stage import Stage
import numpy as np

class TCTStages:
	def __init__(self, x_stage_port='COM3', y_stage_port='COM4', z_stage_port='COM5'):
		self.x_stage = Stage(port=x_stage_port)
		self.y_stage = Stage(port=y_stage_port)
		self.z_stage = Stage(port=z_stage_port)
		self._stages = [self.x_stage, self.y_stage, self.z_stage]
	
	def move_to(self, x=None, y=None, z=None):
		for stage, pos in zip(self._stages, [x,y,z]):
			if pos == None:
				continue
			stage.move_to(pos,blocking=True)
	
	def move_rel(self, x=None, y=None, z=None):
		for stage, dist in zip(self._stages, [x,y,z]):
			if dist == None or dist == 0:
				continue
			stage.move_rel(dist,blocking=True)
	
	@property
	def position(self):
		return tuple([stage.position for stage in self._stages])
