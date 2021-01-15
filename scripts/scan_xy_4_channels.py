from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.utils import save_4ch_trigger # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

def script_core(measurement_name: str, x_start: float, x_end: float, y_start: float, y_end: float, z_focus: float, n_steps: int, n_average_triggers: int = 1):
	for var in [x_start, x_end, y_start, y_end, z_focus]:
		if var > 1: 
			raise ValueError(f'Check the values of x_start, x_end, y_start, y_end and z_focus. One of them is {var} which is more than one meter, this has to be wrong.')
	bureaucrat = Bureaucrat(
		str(Path(f'C:/Users/tct_cms/Desktop/TCT_measurements_data/{measurement_name}')),
		variables = locals(),
		new_measurement = True,
	)
	
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	stages = TCTStages()

	print('Moving to start position...')
	stages.move_to(
		x = x_start,
		y = y_start,
		z = z_focus,
	)
	
	for nx,x_position in enumerate(np.linspace(x_start,x_end,n_steps)):
		for ny,y_position in enumerate(np.linspace(y_start,y_end,n_steps)):
			print('#############################')
			print(f'nx, ny = {nx}, {ny}')
			print(f'Moving stages to {(x_position,y_position)} m...')
			stages.move_to(
				x = x_position,
				y = y_position,
			)
			print(f'Current position is {stages.position} m')
			print('Acquiring signals...')
			sleep(0.01)
			averaged_signals = {}
			for n_average in range(n_average_triggers):
				signals = osc.acquire_one_pulse()
				if n_average == 0:
					for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
						averaged_signals[ch] = signals[ch]
						averaged_signals[ch]['volt'] = np.array(averaged_signals[ch]['volt'])
				else:
					for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
						averaged_signals[ch]['volt'] += np.array(signals[ch]['volt'])
			for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
				averaged_signals[ch]['volt'] /= n_average_triggers
			
			fname = f'{bureaucrat.raw_data_dir_path}/{nx:05d}-{ny:05d}.txt'
			print(f'Saving data in "{fname}"...')
			save_4ch_trigger(
				fname = fname,
				position = stages.position,
				data = averaged_signals,
			)
			temp_fig = mpl.manager.new(
				title = f'Raw signals for nx={nx} and ny={ny}',
				subtitle = f'Measurement {bureaucrat.measurement_name}',
				xlabel = 'Time (s)',
				ylabel = 'Amplitude (V)',
				package = 'plotly' if np.random.rand() < 20/n_steps**2 else 'matplotlib',
			)
			for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
				temp_fig.plot(
					averaged_signals[ch]['time'],
					averaged_signals[ch]['volt'],
					label = ch,
				)
			mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/raw_signals_plots')
			mpl.manager.delete_all_figs()
				
	print('Finished measuring! :)')

############################################################

if __name__ == '__main__':
	import sys
	sys.path.append(str(Path('C:/Users/tct_cms/Desktop/phd-scripts/ac-lgad')))
	from parse_raw_data import script_core as parse_raw_data
	from plot_parsed_data import script_core as plot_parsed_data
	
	measurement_names = input('Measurement name? ').replace(' ', '_')
	while True:
		print('Starting a new measurement...')
		script_core(
			measurement_name = measurement_names,
			x_start = 21.232617187499997e-3 - 500e-6,
			x_end = 21.232617187499997e-3 + 500e-6,
			y_start = 37.164013671875004e-3 - 500e-6,
			y_end = 37.164013671875004e-3 + 500e-6,
			n_steps = 111,
			z_focus = 54.27e-3,
			n_average_triggers = 5,
		)
		print('Parsing raw data...')
		parse_raw_data(
			str(sorted(list(Path('C:/Users/tct_cms/Desktop/TCT_measurements_data').iterdir()))[-1]),
		)
		print('Plotting parsed data...')
		plot_parsed_data(
			str(sorted(list(Path('C:/Users/tct_cms/Desktop/TCT_measurements_data').iterdir()))[-1]),
		)
