import os
from time import sleep
import datetime
from shutil import copyfile
import __main__

def get_timestamp():
	sleep(1) # This ensures that there will not exist two equal timestamps.
	return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

class Bureaucrat:
	def __init__(self, measurement_name, prepend_timestamp=True, measurements_base_path='C:/Users/tct_cms/Desktop/TCT_measurements_data'):
		
		self._measurement_name = f'{get_timestamp()}_' if prepend_timestamp == True else ''
		self._measurement_name += measurement_name
		self._measurements_base_path = measurements_base_path
		
		self.create_dir_structure_for_new_measurement()
		
		copyfile(
			os.path.join(os.getcwd(), __main__.__file__),
			os.path.join(self.scripts_dir_path, __main__.__file__)
		)
		with open(os.path.join(self.scripts_dir_path, __main__.__file__), 'r+') as f:
			content = f.read()
			f.seek(0, 0)
			f.write(f'# This is a copy of the script used to measure. This copy was automatically made by The Bureaucrat')


	def create_dir_structure_for_new_measurement(self):
		dirs = [
			self.raw_data_dir_path,
			self.processed_data_dir_path,
			self.scripts_dir_path,
		]
		for d in dirs:
			if not os.path.isdir(d):
				os.makedirs(d)
	@property
	def measurement_name(self):
		return self._measurement_name
	@property
	def measurements_base_path(self):
		return self._measurements_base_path
	@property
	def measurement_path(self):
		return f'{self.measurements_base_path}/{self.measurement_name}'
	@property
	def raw_data_dir_path(self):
		return f'{self.measurement_path}/raw'
	@property
	def processed_data_dir_path(self):
		return f'{self.measurement_path}/processed'
	@property
	def scripts_dir_path(self):
		return os.path.join(self.measurement_path, 'scripts')

	
