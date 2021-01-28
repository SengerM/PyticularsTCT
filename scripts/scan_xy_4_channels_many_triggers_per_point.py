from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
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
	
	ofile_path = bureaucrat.processed_data_dir_path/Path('measured_data.csv')
	with open(ofile_path, 'w') as ofile:
		print(f'n_x\tn_y\tn_trigger\tx (m)\ty (m)\tz (m)\tn_channel\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tt_10 (s)\tt_50 (s)\tt_90 (s)\tTime over 20 % threshold (s)', file = ofile)
	
	for nx,x_position in enumerate(np.linspace(x_start,x_end,n_steps)):
		for ny,y_position in enumerate(np.linspace(y_start,y_end,n_steps)):
			print('#############################')
			print(f'nx, ny = {nx}, {ny}')
			stages.move_to(
				x = x_position,
				y = y_position,
			)
			print(f'Current xyz position is {stages.position} m')
			print('Acquiring and processing signals...')
			sleep(0.1)
			for n in range(n_triggers):
				position = stages.position
				n_attempts = 0
				success = [False]*len(CHANNELS)
				while not all(success) and n_attempts < 5:
					n_attempts += 1
					raw_data = osc.acquire_one_pulse()
					success = [False]*len(CHANNELS)
					for idx,ch in enumerate(CHANNELS):
						try: # Try to calculate all the quantities of interest.
							s = LGADSignal(
								time = raw_data[ch]['time'],
								samples = raw_data[ch]['volt'],
							)
							s.amplitude
							s.noise
							s.risetime
							s.collected_charge()
							s.time_at(10)
							s.time_at(50)
							s.time_at(90)
							s.time_over_threshold(20)
						except:
							print(f'Unable to parse at nx,ny = {nx},{ny} for {ch}, trigger number {n}, I will try {5-n_attempts} times more.')
							break
						else:
							success[idx] = True
				if not all(success): 
					print(f'Unable to save data at nx,ny = {nx},{ny}, trigger number {n}. I will skip this point.')
					continue
				# If we are here it is because the data from all the triggers is good:
				for idx,ch in enumerate(CHANNELS):
					s = LGADSignal(
						time = raw_data[ch]['time'],
						samples = raw_data[ch]['volt'],
					)
					with open(ofile_path, 'a') as ofile:
						print(f'{nx}\t{ny}\t{n}\t{position[0]:.6e}\t{position[1]:.6e}\t{position[2]:.6e}\t{idx+1}\t{s.amplitude:.6e}\t{s.noise:.6e}\t{s.risetime:.6e}\t{s.collected_charge():.6e}\t{s.time_at(10):.6e}\t{s.time_at(50):.6e}\t{s.time_at(90):.6e}\t{s.time_over_threshold(20):.6e}', file = ofile)
					if np.random.rand() < 20/n_steps**2/n_triggers/4:
						fig = mpl.manager.new(
							title = f'Signal at {nx:05d}-{ny:05d}  n_trigg={n} {ch}',
							subtitle = f'Measurement: {bureaucrat.measurement_name}',
							xlabel = 'Time (s)',
							ylabel = 'Amplitude (V)',
							package = 'plotly',
						)
						s.plot_myplotlib(fig)
						mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/some_random_processed_signals_plots')
						mpl.manager.delete_all_figs()
				
	print('Finished measuring! :)')

########################################################################

if __name__ == '__main__':
	
	X_START = 21.13607e-3
	X_END = 21.3e-3
	Y_START = 37.09193e-3
	Y_END = 37.26648e-3
	
	STEP_SIZE = 5e-6
	
	n_steps = int(max([
		(X_END-X_START)/STEP_SIZE,
		(Y_END-Y_START)/STEP_SIZE,
	]))
	
	if input(f'The number of steps is {n_steps}. Continue? yes/no ') != 'yes':
		print('Exiting...')
		exit()
	
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		x_start = X_START,
		x_end = X_END,
		y_start = Y_START,
		y_end = Y_END,
		n_steps = n_steps,
		z_focus = 54.54e-3,
		n_triggers = 333,
	)
