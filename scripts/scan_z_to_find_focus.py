from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.utils import save_4ch_trigger # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import os
import myplotlib as mpl
from PyticularsTCT.utils import save_tct_trigger, read_tct_trigger
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
import random
from data_processing_bureaucrat.Bureaucrat import Bureaucrat # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

############################################################

N_STEPS = 333
X_POSITION = 21.15977e-3
Y_POSITION = 37.32302e-3
Z_START = 49.3e-3
Z_END = 58e-3
N_AVERAGE_TRIGGERS = 11

############################################################

bureaucrat = Bureaucrat(
	str(Path(f'C:/Users/tct_cms/Desktop/TCT_measurements_data/{input("Measurement name? ")}')),
	variables = locals(),
	new_measurement = True,
)

def measure():
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	stages = TCTStages()

	print('Moving to start position...')
	stages.move_to(
		z = Z_START,
		x = X_POSITION,
		y = Y_POSITION,
	)
	print(f'Current position is {stages.position} m')
	print('Measuring...')
	
	for nz,z in enumerate(np.linspace(Z_START,Z_END,N_STEPS)):
		print('#############################')
		print(f'nz = {nz}')
		stages.move_to(z=z)
		print(f'Current position is {stages.position} m')
		print('Acquiring signals...')
		sleep(0.01)
		osc.trig_mode = 'AUTO'
		sleep(0.01)
		osc.trig_mode = 'SINGLE'
		data = osc.get_wf(CH=1)
		averaged_signal = np.array(data['volt'])
		for n_average in range(N_AVERAGE_TRIGGERS):
			osc.trig_mode = 'AUTO'
			sleep(0.01)
			osc.trig_mode = 'SINGLE'
			data = osc.get_wf(CH=1)
			averaged_signal += np.array(data['volt'])
		averaged_signal /= N_AVERAGE_TRIGGERS
		
		fname = f'{bureaucrat.raw_data_dir_path}/{nz:05d}.txt'.replace("/","\\")
		print(f'Saving data in {fname}...')
		save_tct_trigger(
			fname = fname,
			position = stages.position,
			time = data['time'],
			ch1 = averaged_signal,
		)
		temp_fig = mpl.manager.new(
			title = f'Raw signal for nz={nz}',
			xlabel = 'Time (s)',
			ylabel = 'Amplitude (V)',
		)
		temp_fig.plot(
			data['time'],
			averaged_signal,
		)
		mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/raw_signals_plots')
		mpl.manager.delete_all_figs()
			
	print('Finished measuring! :)')

def parse_amplitudes():
	print('Reading data...')
	raw_data = []
	for fname in sorted(os.listdir(bureaucrat.raw_data_dir_path)):
		raw_data.append(read_tct_trigger(f'{bureaucrat.raw_data_dir_path}/{fname}'))
	
	print('Calculating amplitudes...')
	amplitudes = []
	zs = []
	for data in raw_data:
		zs.append(data['position'][2])
		ch = list(data['volt'].keys())[0] # CH1, CH2, etc...
		signal = LGADSignal(
			time = data['time'],
			samples = data['volt'][ch]*-1,
		)
		amplitudes.append(signal.amplitude)
	
	fname = f'{bureaucrat.processed_data_dir_path}/amplitude_vs_z.txt'
	print(f'Saving parsed data to file {fname}...')
	with open(fname, 'w') as ofile:
		print('#z (m)\tAmplitude (V)', file = ofile)
		for z,A in zip(zs, amplitudes):
			print(f'{z}\t{A}', file=ofile)

def plot_amplitudes():
	data = np.genfromtxt(f'{bureaucrat.processed_data_dir_path}/amplitude_vs_z.txt').transpose()
	z = data[0]
	amplitude = data[1]
	mpl.manager.set_plotting_package('plotly')
	fig = mpl.manager.new(
		title = f'Focus find for PIN diode at x = {X_POSITION} and y = {Y_POSITION}',
		xlabel = 'z position (m)',
		ylabel = 'Amplitude (V)',
		package = 'plotly',
	)
	fig.plot(
		z,
		amplitude,
		marker = '.',
		label = 'Measured data',
	)
	
	fig.save(f'{bureaucrat.processed_data_dir_path}/plot.pdf')
	mpl.manager.show()

if __name__ == '__main__':
	print('Measuring...')
	measure()
	print('Parsing amplitudes...')
	parse_amplitudes()
	print('Plotting amplitudes...')
	plot_amplitudes()
