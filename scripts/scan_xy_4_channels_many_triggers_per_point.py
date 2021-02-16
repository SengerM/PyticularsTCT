from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramProgressBar # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

CHANNELS = ['CH1', 'CH2', 'CH3', 'CH4']

def acquire_nice_signals(osc, n_attempts=5, channels=CHANNELS):
	n_attempts = int(n_attempts)
	success = {}
	for ch in channels:
		success[ch] = False
	while n_attempts > 0 and not all([success[ch] for ch in channels]):
		n_attempts -= 1
		for ch in channels: success[ch] = False
		raw_data = osc.acquire_one_pulse()
		signals = {}
		for ch in channels:
			signals[ch] = LGADSignal(
				time = raw_data[ch]['time'],
				samples = -1*raw_data[ch]['volt'],
			)
			success[ch] = signals[ch].worth
	if all([success[ch] for ch in channels]):
		return signals
	else:
		return None

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
	
	with TelegramProgressBar(n_steps**2*n_triggers, bureaucrat) as pbar:
		for nx,x_position in enumerate(np.linspace(x_start,x_end,n_steps)):
			for ny,y_position in enumerate(np.linspace(y_start,y_end,n_steps)):
				stages.move_to(
					x = x_position,
					y = y_position,
				)
				sleep(0.1)
				for n in range(n_triggers):
					pbar.update(1)
					position = stages.position
					signals = acquire_nice_signals(osc, n_attempts = 1)
					if signals is None:
						continue
					for idx,ch in enumerate(CHANNELS):
						s = signals[ch]
						with open(ofile_path, 'a') as ofile:
							print(
								f'{nx}\t{ny}\t{n}\t{position[0]:.6e}\t{position[1]:.6e}\t{position[2]:.6e}\t{idx+1}\t{s.amplitude:.6e}\t{s.noise:.6e}\t{s.risetime:.6e}\t{s.collected_charge():.6e}\t{s.time_at(10):.6e}\t{s.time_at(50):.6e}\t{s.time_at(90):.6e}\t{s.time_over_threshold(20):.6e}', 
								file = ofile,
							)
					if np.random.rand() < 20/n_steps**2/n_triggers:
						for idx,ch in enumerate(CHANNELS):
							fig = mpl.manager.new(
								title = f'Signal at {nx:05d}-{ny:05d}  n_trigg={n} {ch}',
								subtitle = f'Measurement: {bureaucrat.measurement_name}',
								xlabel = 'Time (s)',
								ylabel = 'Amplitude (V)',
								package = 'plotly',
							)
							signals[ch].plot_myplotlib(fig)
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
		z_focus = 54.428e-3,
		n_triggers = 33,
	)
