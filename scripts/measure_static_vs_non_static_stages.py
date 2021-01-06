from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.utils import save_4ch_trigger # https://github.com/SengerM/PyticularsTCT
import numpy as np
import time
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

def script_core(measurement_name: str, x_position: float, y_position: float, z_focus: float, n_shots: int):
	for var in [x_position, y_position, z_focus]:
		if var > 1: 
			raise ValueError(f'Check the values of x_position, y_position and z_focus. One of them is {var} which is more than one meter, this has to be wrong.')
	print('Starting a new measurement...')
	bureaucrat = Bureaucrat(
		str(Path(f'C:/Users/tct_cms/Desktop/TCT_measurements_data/{measurement_name}')),
		variables = locals(),
		new_measurement = True,
	)
	
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	stages = TCTStages()

	stages.move_to(
		x = x_position,
		y = y_position,
		z = z_focus,
	)
	
	print(f'Moving stages to {(x_position,y_position)} m...')
	stages.move_to(
		x = x_position,
		y = y_position,
	)
	time.sleep(.5)
	print(f'Current position is {stages.position} m')
	print('Acquiring static shots...')
	dir_for_raw_data = f'{bureaucrat.processed_data_dir_path}/static_stages_raw_data/'
	Path(dir_for_raw_data).mkdir()
	for n in range(n_shots):
		print('Acquiring signals...')
		acquired_data = osc.acquire_one_pulse()
		fname = f'{dir_for_raw_data}/{n:05d}.txt'
		print(f'Saving data in "{fname}"...')
		save_4ch_trigger(
			fname = fname,
			position = stages.position,
			data = acquired_data,
		)
		fig = mpl.manager.new(
			title = f'Raw signals for n={n} with static stages',
			subtitle = f'Measurement {bureaucrat.measurement_name}',
			xlabel = 'Time (s)',
			ylabel = 'Amplitude (V)',
			package = 'plotly' if np.random.rand() < 20/(n+1) else 'matplotlib',
		)
		for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
			fig.plot(
				acquired_data[ch]['time'],
				acquired_data[ch]['volt'],
				label = ch,
			)
		mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/static_stages_raw_plots')
	
	print('Acquiring non-static shots...')
	dir_for_raw_data = f'{bureaucrat.processed_data_dir_path}/non_static_stages_raw_data/'
	Path(dir_for_raw_data).mkdir()
	for n in range(n_shots):
		random_x = 500e-6*np.random.randn()
		random_y = 500e-6*np.random.randn()
		print(f'Moving stages to random position x,y = {(x_position+random_x, y_position+random_y)} m...')
		stages.move_to(
			x = x_position + random_x,
			y = y_position + random_y,
		)
		time.sleep(.1)
		print(f'Moving stages back to {(x_position,y_position)} m...')
		stages.move_to(
			x = x_position,
			y = y_position,
		)
		time.sleep(.1)
		print('Acquiring signals...')
		acquired_data = osc.acquire_one_pulse()
		fname = f'{dir_for_raw_data}/{n:05d}.txt'
		print(f'Saving data in "{fname}"...')
		save_4ch_trigger(
			fname = fname,
			position = stages.position,
			data = acquired_data,
		)
		fig = mpl.manager.new(
			title = f'Raw signals for n={n} with non-static stages',
			subtitle = f'Measurement {bureaucrat.measurement_name}',
			xlabel = 'Time (s)',
			ylabel = 'Amplitude (V)',
			package = 'plotly' if np.random.rand() < 20/(n+1) else 'matplotlib',
		)
		for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
			fig.plot(
				acquired_data[ch]['time'],
				acquired_data[ch]['volt'],
				label = ch,
			)
		mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/non_static_stages_raw_plots')
				
	print('Finished measuring! :)')

############################################################

if __name__ == '__main__':
	print('Hello')
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		x_position = 21.27775e-3,
		y_position = 37.37152e-3,
		z_focus = 54.5e-3,
		n_shots = 2222,
	)
