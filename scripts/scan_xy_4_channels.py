from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.utils import save_4ch_trigger # https://github.com/SengerM/PyticularsTCT
import numpy as np
from time import sleep
import os
import myplotlib as mpl
from PyticularsTCT.utils import read_4ch_trigger
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from myplotlib.utils import get_timestamp
import random
from bureaucrat import Bureaucrat

############################################################

# (0.021295419921875, 0.038191191406250005, 0.056478310546875)

X_START = 21.206e-3
X_END = 21.382e-3
Y_START = 38.093e-3
Y_END = 38.282e-3
N_STEPS = 33
Z_FOCUS = 0.05467107
N_AVERAGE_TRIGGERS = 1

############################################################

bureaucrat = Bureaucrat(
	measurement_name = str(input('Measurement name? ')).replace(' ', '_')
)
print(f'Data will be saved in {bureaucrat.measurement_path}')

def measure():
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	stages = TCTStages()

	print('Moving to start position...')
	stages.move_to(
		x = X_START,
		y = Y_START,
		z = Z_FOCUS
	)
	print(f'Current position is {stages.position} m')
	print('Measuring...')
	
	for nx,x_position in enumerate(np.linspace(X_START,X_END,N_STEPS)):
		for ny,y_position in enumerate(np.linspace(Y_START,Y_END,N_STEPS)):
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
			for n_average in range(N_AVERAGE_TRIGGERS):
				signals = osc.acquire_one_pulse()
				if n_average == 0:
					for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
						averaged_signals[ch] = signals[ch]
						averaged_signals[ch]['volt'] = np.array(averaged_signals[ch]['volt'])
				else:
					for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
						averaged_signals[ch]['volt'] += np.array(signals[ch]['volt'])
			for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
				averaged_signals[ch]['volt'] /= N_AVERAGE_TRIGGERS
			
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
				package = 'plotly' if np.random.rand() < 20/N_STEPS**2 else 'matplotlib',
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

def parse_amplitudes():
	print('Reading data...')
	raw_data = []
	for fname in sorted(os.listdir(bureaucrat.raw_data_dir_path)):
		raw_data.append(read_4ch_trigger(f'{bureaucrat.raw_data_dir_path}/{fname}'))
	
	x_positions = [data['position'][0] for data in raw_data]
	x_positions = sorted(list(set(x_positions))) # Remove duplicate elements.
	y_positions = [data['position'][1] for data in raw_data]
	y_positions = sorted(list(set(y_positions))) # Remove duplicate elements.
	
	print('Calculating amplitudes...')
	amplitudes = {
		'CH1': np.zeros((len(x_positions),len(y_positions))),
		'CH2': np.zeros((len(x_positions),len(y_positions))),
		'CH3': np.zeros((len(x_positions),len(y_positions))),
		'CH4': np.zeros((len(x_positions),len(y_positions))),
	}
	for data in raw_data:
		nx = x_positions.index(data['position'][0])
		ny = y_positions.index(data['position'][1])
		for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
			signal = LGADSignal(
				time = data[ch]['time'],
				samples = data[ch]['volt']*-1,
			)
			amplitudes[ch][nx,ny] = signal.amplitude
	
	print('Saving parsed data to files...')
	np.savetxt(f'{bureaucrat.processed_data_dir_path}/x_positions.txt', x_positions)
	np.savetxt(f'{bureaucrat.processed_data_dir_path}/y_positions.txt', y_positions)
	for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
		np.savetxt(f'{bureaucrat.processed_data_dir_path}/amplitudes_{ch}.txt', amplitudes[ch])

def plot_amplitudes():
	x_positions = np.genfromtxt(f'{bureaucrat.processed_data_dir_path}/x_positions.txt')
	y_positions = np.genfromtxt(f'{bureaucrat.processed_data_dir_path}/y_positions.txt')
	amplitudes = {}
	for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
		amplitudes[ch] = np.genfromtxt(f'{bureaucrat.processed_data_dir_path}/amplitudes_{ch}.txt').transpose()
	xx, yy = np.meshgrid(x_positions, y_positions)
	for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
		fig = mpl.manager.new(
			title = f'{ch} amplitude colormap',
			subtitle = f'Measurement {bureaucrat.measurement_name}',
			xlabel = '$x$ position (mm)',
			ylabel = '$y$ position (mm)',
			aspect = 'equal',
			package = 'plotly',
		)
		fig.colormap(
			x = xx*1e3,
			y = yy*1e3,
			z = amplitudes[ch],
		)
	mpl.manager.save_all(mkdir=f'{bureaucrat.processed_data_dir_path}/amplitude colormaps plots')
	mpl.manager.show()

############################################################

if __name__ == '__main__':
	print('Measuring...')
	measure()
	print('Parsing amplitudes...')
	parse_amplitudes()
	print('Plotting amplitudes...')
	plot_amplitudes()
	print(f'Data was saved in {bureaucrat.measurement_path}')
