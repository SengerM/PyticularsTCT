from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.utils import save_4ch_trigger # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

CHANNELS = ['CH1', 'CH2', 'CH3', 'CH4']

def script_core(
	measurement_name: str, 
	x_start: float, 
	x_end: float, 
	y_start: float, 
	y_end: float, 
	z_focus: float, 
	n_steps: int, 
	n_triggers: int = 1,
):
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
			print(f'Saving position of stages in data files...')
			ofpaths = {}
			for ch in CHANNELS:
				parent = Path(f'{bureaucrat.processed_data_dir_path}/{ch}')
				parent.mkdir(exist_ok = True)
				ofpaths[ch] = Path(f'{parent}/{nx:05d}-{ny:05d}.txt')
				with open(ofpaths[ch], 'w') as ofile:
					print(f'# x_position = {stages.position[0]}', file = ofile)
					print(f'# y_position = {stages.position[1]}', file = ofile)
					print(f'# z_position = {stages.position[2]}', file = ofile)
					print(f'# n_trigger\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tt_10 (s)\tt_50 (s)\tt_90 (s)\tTime over 20 % threshold (s)', file = ofile)
			
			print('Acquiring and processing signals...')
			sleep(0.1)
			for n in range(n_triggers):
				raw_data = osc.acquire_one_pulse()
				for ch in CHANNELS:
					s = LGADSignal(
						time = raw_data[ch]['time'],
						samples = raw_data[ch]['volt'],
					)
					with open(ofpaths[ch], 'a') as ofile:
						try:
							print(f'{n}\t{s.amplitude}\t{s.noise}\t{s.risetime}\t{s.collected_charge()}\t{s.time_at(10)}\t{s.time_at(50)}\t{s.time_at(90)}\t{s.time_over_threshold(20)}', file = ofile)
						except:
							print(f'Unable to parse at nx,ny = {nx},{ny} for {ch}, trigger number {n}, I will just continue.')
					if np.random.rand() < 20/n_steps**2/n_triggers/4:
						fig = mpl.manager.new(
							title = f'Signal at {nx:05d}-{ny:05d} {ch} n_trigg={n}',
							subtitle = f'Measurement: {bureaucrat.measurement_name}',
							xlabel = 'Time (s)',
							ylabel = 'Amplitude (V)',
							package = 'plotly',
						)
						s.plot_myplotlib(fig)
						mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/some_random_processed_signals_plots')
						mpl.manager.delete_all_figs()
				
	print('Finished measuring! :)')

############################################################

if __name__ == '__main__':
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		x_start = 21.17e-3,
		x_end = 21.30e-3,
		y_start = 37.31e-3,
		y_end = 37.44e-3,
		n_steps = 7,
		z_focus = 54.5e-3,
		n_triggers = 333,
	)
