from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramReportingInformation # https://github.com/SengerM/data_processing_bureaucrat
from progressreporting.TelegramProgressReporter import TelegramProgressReporter as TReport # https://github.com/SengerM/progressreporting
from pathlib import Path
import pandas

CHANNELS = ['CH1']
TIMES_AT = []

def script_core(measurement_name: str, n_steps: int, z_start: float, z_end: float, n_triggers: int = 1):
	for var in [z_start, z_end]:
		if var > 1: 
			raise ValueError(f'Check the values of z_start and z_end. One of them is {var} which is more than one meter, this has to be wrong.')
	bureaucrat = Bureaucrat(
		str(Path(f'C:/Users/tct_cms/Desktop/TCT_measurements_data/{measurement_name}')),
		variables = locals(),
		new_measurement = True,
	)
	
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	stages = TCTStages()

	print('Moving to start position...')
	stages.move_to(z = z_start)
	
	ofile_path = bureaucrat.processed_data_dir_path/Path('measured_data.csv')
	with open(ofile_path, 'w') as ofile:
		string = f'n_z\tn_trigger\tx (m)\ty (m)\tz (m)\tn_channel\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tTime over noise (s)'
		for pp in TIMES_AT:
			string += f'\tt_{pp} (s)'
		print(string, file = ofile)
	
	with TReport(total=n_steps*n_triggers+1, title=f'{bureaucrat.measurement_name}', telegram_token=TelegramReportingInformation().token, telegram_chat_id=TelegramReportingInformation().chat_id) as pbar:
		with open(ofile_path, 'a') as ofile:
			for nz,z_position in enumerate(np.linspace(z_start,z_end,n_steps)):
				stages.move_to(z = z_position)
				sleep(0.1)
				for n in range(n_triggers):
					print(f'Preparing to acquire signals at nz={nz}, n_trigger={n}...')
					position = stages.position
					raw_data = osc.acquire_one_pulse()
					signals = {}
					for idx,ch in enumerate(CHANNELS):
						signals[ch] = LGADSignal(
							time = raw_data[ch]['time'],
							samples = raw_data[ch]['volt'],
						)
						string = f'{nz}\t{n}\t{position[0]:.6e}\t{position[1]:.6e}\t{position[2]:.6e}\t{idx+1}'
						string += f'\t{signals[ch].amplitude:.6e}\t{signals[ch].noise:.6e}\t{signals[ch].rise_time:.6e}\t{signals[ch].collected_charge:.6e}\t{signals[ch].time_over_noise:.6e}'
						for pp in TIMES_AT:
							try:
								string += f'\t{signals[ch].find_time_at_rising_edge(pp):.6e}'
							except:
								string += f'\t{float("NaN")}'
						print(string, file = ofile)
					if np.random.rand() < 20/n_steps**2/n_triggers:
						for idx,ch in enumerate(CHANNELS):
							fig = mpl.manager.new(
								title = f'Signal at nz {nz:05d} n_trigg {n} {ch}',
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
							mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/some_random_processed_signals_plots')
				pbar.update(n_triggers)
		print('Finished measuring! :)')
		
		print('Making the plot...')
		data = pandas.read_csv(
			ofile_path,
			delimiter = '\t',
		)
		z_values = sorted(set(data['z (m)']))
		mean_amplitude = []
		for z in z_values:
			mean_amplitude.append(np.nanmean(data[(data['z (m)']==z) & data['n_channel']==1]['Amplitude (V)']))
		
		fig = mpl.manager.new(
			title = f'Finding the focus',
			subtitle = f'Data set: {bureaucrat.measurement_name}',
			xlabel = 'z (m)',
			ylabel = 'Amplitude (V)',
		)
		fig.plot(
			z_values,
			mean_amplitude,
			marker = '.',
		)
		mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path)
		pbar.update(1)

########################################################################

if __name__ == '__main__':
	
	Z_START = 54.1791015625e-3 - 1e-2
	Z_END = Z_START + 2e-2
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		n_steps = 333,
		z_start = Z_START,
		z_end = Z_END,
		n_triggers = 33,
	)
