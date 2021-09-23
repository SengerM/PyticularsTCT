from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramReportingInformation # https://github.com/SengerM/data_processing_bureaucrat
from progressreporting.TelegramProgressReporter import TelegramReporter # https://github.com/SengerM/progressreporting
from pathlib import Path
from plotting_scripts.plot_everything_from_linear_scan import script_core as plot_everything_from_linear_scan

CHANNELS = ['CH1', 'CH2', 'CH3', 'CH4']
TIMES_AT = [10,20,30,40,50,60,70,80,90]

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
		if var**2 > 1: 
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
		string = f'n_pos\tn_trigger\tx (m)\ty (m)\tz (m)\tn_channel\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tTime over noise (s)'
		for pp in TIMES_AT:
			string += f'\tt_{pp} (s)'
		print(string, file = ofile)
	
	x_positions = np.linspace(x_start,x_end,n_steps)
	y_positions = np.linspace(y_start,y_end,n_steps)
	reporter = TelegramReporter(
		telegram_token = TelegramReportingInformation().token, 
		telegram_chat_id = TelegramReportingInformation().chat_id,
	)
	with reporter.report_for_loop(n_steps*n_triggers, f'{bureaucrat.measurement_name}') as reporter:
		with open(ofile_path, 'a') as ofile:
			for n_pos,xy_position in enumerate([(x,y) for x,y in zip(x_positions,y_positions)]):
				stages.move_to(
					x = xy_position[0],
					y = xy_position[1],
				)
				sleep(0.1)
				position = stages.position
				for n in range(n_triggers):
					print(f'Preparing to acquire signals at n_pos={n_pos}, n_trigger={n}...')
					raw_data = osc.acquire_one_pulse()
					signals = {}
					for idx,ch in enumerate(CHANNELS):
						signals[ch] = LGADSignal(
							time = raw_data[ch]['time'],
							samples = -1*raw_data[ch]['volt'],
						)
						string = f'{n_pos}\t{n}\t{position[0]:.6e}\t{position[1]:.6e}\t{position[2]:.6e}\t{idx+1}'
						string += f'\t{signals[ch].amplitude:.6e}\t{signals[ch].noise:.6e}\t{signals[ch].rise_time:.6e}\t{signals[ch].collected_charge:.6e}\t{signals[ch].time_over_noise:.6e}'
						for pp in TIMES_AT:
							try:
								string += f'\t{signals[ch].find_time_at_rising_edge(pp):.6e}'
							except:
								string += f'\t{float("NaN")}'
						print(string, file = ofile)
					if np.random.rand() < 20/n_steps/n_triggers:
						for idx,ch in enumerate(CHANNELS):
							fig = mpl.manager.new(
								title = f'Signal at {n_pos:05d} n_trigg {n} {ch}',
								subtitle = f'Measurement: {bureaucrat.measurement_name}',
								xlabel = 'Time (s)',
								ylabel = 'Amplitude (V)',
								package = 'plotly',
							)
							signals[ch].plot_myplotlib(fig)
							for pp in TIMES_AT:
								try:
									fig.plot(
										[signals[ch].find_time_at_rising_edge(pp)],
										[signals[ch].signal_at(signals[ch].find_time_at_rising_edge(pp))],
										marker = 'x',
										linestyle = '',
										label = f'Time at {pp} %',
										color = (0,0,0),
									)
								except:
									pass
							mpl.manager.save_all(mkdir=bureaucrat.processed_data_dir_path/Path('some_random_processed_signals_plots'))
					reporter.update(1)
	print('Finished measuring! :)')
	print('Doing plots...')
	plot_everything_from_linear_scan(directory = bureaucrat.measurement_base_path)
	print('Finished plotting!')

########################################################################

if __name__ == '__main__':
	
	Y_STOP = 29.87547e-3 + 11e-6
	Y_START = 29.67548e-3
	X_FIXED = (24.71717e-3+24.7054e-3)/2
	STEP_SIZE = 1e-6
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		x_start = X_FIXED,
		x_end = X_FIXED,
		y_start = Y_START,
		y_end = Y_STOP,
		n_steps = int(((Y_STOP-Y_START)**2)**.5/STEP_SIZE),
		z_focus = 53.26016601562499e-3,
		n_triggers = 3333,
		)

