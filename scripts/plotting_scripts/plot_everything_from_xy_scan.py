from data_processing_bureaucrat.Bureaucrat import Bureaucrat
import numpy as np
from pathlib import Path
import myplotlib as mpl
import pandas

CHANNELS = [f'CH{i}' for i in [1,2,3,4]]
STATISTICAL_QUANTITIES = ['mean']

def script_core(directory):
	bureaucrat = Bureaucrat(
		directory,
		variables = locals(),
	)
	
	try:
		data = pandas.read_feather(bureaucrat.processed_by_script_dir_path('scan_xy_4_channels_many_triggers_per_point.py')/Path('measured_data.fd'))
	except FileNotFoundError:
		data = pandas.read_csv(
			bureaucrat.processed_by_script_dir_path('scan_xy_4_channels_many_triggers_per_point.py')/Path('measured_data.csv'),
			sep = '\t',
			low_memory = False,
		)

	nx_values = sorted(set(data['n_x']))
	ny_values = sorted(set(data['n_y']))
	x_values = sorted(set(data['x (m)']))
	y_values = sorted(set(data['y (m)']))
	xx, yy = np.meshgrid(x_values, y_values)
	channels = [f'CH{i}' for i in sorted(set(data['n_channel']))]
	if 'n_pulse' not in data:
		# I add this to make more uniform the processing later on.
		data['n_pulse'] = [1 for i in range(len(data['n_x']))]
	pulses = [f'pulse {i}' for i in sorted(set(data['n_pulse']))]
	
	for column in data:
		if column in ['n_x', 'n_y', 'n_trigger', 'x (m)', 'y (m)', 'z (m)', 'n_channel', 'n_pulse']:
			continue
		column_matrices = {}
		for stat in STATISTICAL_QUANTITIES:
			column_matrices[stat] = {}
			for ch in channels:
				column_matrices[stat][ch] = {}
				for pulse in pulses:
					column_matrices[stat][ch][pulse] = np.zeros(xx.shape)
					column_matrices[stat][ch][pulse][:] = float('NaN')
					if stat == 'mean':
						column_matrices[stat][ch][pulse] = data.loc[(data['n_channel']==int(ch.replace('CH',''))) & (data['n_pulse']==int(pulse.replace('pulse ','')))].pivot_table(column, 'n_y', 'n_x', aggfunc = np.nanmean)
					elif stat == 'std':
						column_matrices[stat][ch][pulse] = data.loc[(data['n_channel']==int(ch.replace('CH',''))) & (data['n_pulse']==int(pulse.replace('pulse ','')))].pivot_table(column, 'n_y', 'n_x', aggfunc = np.nanstd)
					for package in ['matplotlib', 'plotly']:
						fig = mpl.manager.new(
							title = f'{column[:column.find("(")][:-1]} {ch} {pulse} {stat}',
							subtitle = f'Data set: {bureaucrat.measurement_name}',
							xlabel = 'x (m)',
							ylabel = 'y (m)',
							aspect = 'equal',
							package = package,
						)
						fig.colormap(
							x = xx,
							y = yy,
							z = column_matrices[stat][ch][pulse],
							colorscalelabel = f'{column}',
						)
						mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path/Path('png' if package=='matplotlib' else 'html'))
	
if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Plots every thing measured in an xy scan.')
	parser.add_argument(
		'--dir',
		metavar = 'path', 
		help = 'Path to the base directory of a measurement.',
		required = True,
		dest = 'directory',
		type = str,
	)
	args = parser.parse_args()
	script_core(args.directory)

