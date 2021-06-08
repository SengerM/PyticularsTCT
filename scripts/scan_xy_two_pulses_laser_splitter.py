from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramReportingInformation # https://github.com/SengerM/data_processing_bureaucrat
from progressreporting.TelegramProgressReporter import TelegramProgressReporter as TReport # https://github.com/SengerM/progressreporting
from pathlib import Path

CHANNELS = ['CH1', 'CH2', 'CH3', 'CH4']
TIMES_AT = [10,20,30,40,50,60,70,80,90]
N_PULSES = [1, 2]

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
		string = f'n_x\tn_y\tn_trigger\tx (m)\ty (m)\tz (m)\tn_channel\tn_pulse\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tTime over noise (s)'
		for pp in TIMES_AT:
			string += f'\ttr{pp} (s)'
		for pp in TIMES_AT:
			string += f'\ttf{pp} (s)'
		print(string, file = ofile)
	
	with TReport(
		total=n_steps**2*n_triggers, 
		loop_name=f'{bureaucrat.measurement_name}', 
		telegram_token=TelegramReportingInformation().token, 
		telegram_chat_id=TelegramReportingInformation().chat_id,
	) as reporter:
		with open(ofile_path, 'a') as ofile:
			for nx,x_position in enumerate(np.linspace(x_start,x_end,n_steps)):
				for ny,y_position in enumerate(np.linspace(y_start,y_end,n_steps)):
					stages.move_to(
						x = x_position,
						y = y_position,
					)
					sleep(0.1)
					for n in range(n_triggers):
						reporter.update(1)
						print(f'Preparing to acquire signals at nx={nx}, ny={ny}, n_trigger={n}...')
						position = stages.position
						raw_data = osc.acquire_one_pulse()
						signals = {}
						for n_pulse in N_PULSES:
							signals[n_pulse] = {}
							for idx,ch in enumerate(CHANNELS):
								if n_pulse == 1:
									signals[n_pulse][ch] = LGADSignal(
										time = raw_data[ch]['time'][:int(len(raw_data[ch]['time'])/2)],
										samples = raw_data[ch]['volt'][:int(len(raw_data[ch]['time'])/2)],
									)
								elif n_pulse == 2:
									signals[n_pulse][ch] = LGADSignal(
										time = raw_data[ch]['time'][int(len(raw_data[ch]['time'])/2):],
										samples = raw_data[ch]['volt'][int(len(raw_data[ch]['time'])/2):],
									)
								string = f'{nx}\t{ny}\t{n}\t{position[0]:.6e}\t{position[1]:.6e}\t{position[2]:.6e}\t{idx+1}\t{n_pulse}'
								string += f'\t{signals[n_pulse][ch].amplitude:.6e}\t{signals[n_pulse][ch].noise:.6e}\t{signals[n_pulse][ch].rise_time:.6e}\t{signals[n_pulse][ch].collected_charge:.6e}\t{signals[n_pulse][ch].time_over_noise:.6e}'
								for pp in TIMES_AT:
									try:
										string += f'\t{signals[n_pulse][ch].find_time_at_rising_edge(pp):.6e}'
									except:
										string += f'\t{float("NaN")}'
								for pp in TIMES_AT:
									try:
										string += f'\t{signals[n_pulse][ch].find_time_at_falling_edge(pp):.6e}'
									except:
										string += f'\t{float("NaN")}'
								print(string, file = ofile)
						# Plot -----------------------------------------
						if np.random.rand() < 20/n_steps**2/n_triggers:
							for n_pulse in N_PULSES:
								for idx,ch in enumerate(CHANNELS):
									fig = mpl.manager.new(
										title = f'Signal at {nx:05d}-{ny:05d} n_trigg {n} n_pulse {n_pulse} {ch}',
										subtitle = f'Measurement: {bureaucrat.measurement_name}',
										xlabel = 'Time (s)',
										ylabel = 'Amplitude (V)',
										package = 'plotly',
									)
									signals[n_pulse][ch].plot_myplotlib(fig)
									for pp in TIMES_AT:
										try:
											fig.plot(
												[signals[n_pulse][ch].find_time_at_rising_edge(pp)],
												[signals[n_pulse][ch].signal_at(signals[n_pulse][ch].find_time_at_rising_edge(pp))],
												marker = 'x',
												linestyle = '',
												label = f'tr{pp} % = {signals[n_pulse][ch].find_time_at_rising_edge(pp):.4e} s',
												color = (0,0,0),
											)
										except:
											pass
									for pp in TIMES_AT:
										try:
											fig.plot(
												[signals[n_pulse][ch].find_time_at_falling_edge(pp)],
												[signals[n_pulse][ch].signal_at(signals[n_pulse][ch].find_time_at_falling_edge(pp))],
												marker = 'x',
												linestyle = '',
												label = f'tf{pp} % = {signals[n_pulse][ch].find_time_at_falling_edge(pp):.4e} s',
												color = (0,0,0),
											)
										except:
											pass
							mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/some_random_processed_signals_plots')
					
	print('Finished measuring! :)')

########################################################################

if __name__ == '__main__':
	
	# ~ X_CENTER = -33.68220703125e-3
	# ~ Y_CENTER = -38.392900390625e-3
	# ~ X_WIDTH = 1111e-6
	# ~ Y_WIDTH = X_WIDTH
	
	
	# ~ X_START = X_CENTER - X_WIDTH/2
	# ~ X_END = X_CENTER + X_WIDTH/2
	# ~ Y_START = Y_CENTER - Y_WIDTH/2
	# ~ Y_END = Y_CENTER + Y_WIDTH/2
	
	# ~ X_START = -33.85724e-3
	# ~ X_END = -33.4767e-3
	# ~ Y_START = -38.4309e-3
	# ~ Y_END = -38.0352e-3
	
	X_START = -33.7050e-3
	X_END = -33.3309e-3
	Y_START = -38.5679e-3
	Y_END = -38.1874e-3
	
	STEP_SIZE = 10e-6
	
	n_steps = int(max([
		(X_END-X_START)/STEP_SIZE,
		(Y_END-Y_START)/STEP_SIZE,
	]))
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		x_start = X_START,
		x_end = X_END,
		y_start = Y_START,
		y_end = Y_END,
		n_steps = n_steps,
		z_focus = 55.3044e-3,
		n_triggers = 444,
	)
