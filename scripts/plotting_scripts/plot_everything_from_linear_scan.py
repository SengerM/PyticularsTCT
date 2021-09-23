from data_processing_bureaucrat.Bureaucrat import Bureaucrat
import numpy as np
from pathlib import Path
import myplotlib as mpl
import pandas

STATISTICAL_QUANTITIES = ['mean', 'std']

def script_core(directory):
	bureaucrat = Bureaucrat(
		directory,
		variables = locals(),
	)
	
	data = pandas.read_csv(
		bureaucrat.processed_by_script_dir_path('linear_scan_many_triggers_per_point.py')/Path('measured_data.csv'),
		sep = '\t',
	)
	
	n_poss = sorted(set(data['n_pos']))
	distance = [None]*len(n_poss)
	for n_pos in n_poss:
		if n_pos == 0: 
			distance[n_pos] = 0
			continue
		distance[n_pos] = distance[n_pos-1] + np.linalg.norm(data.loc[data['n_pos']==n_pos,['x (m)', 'y (m)']].iloc[0]-data.loc[data['n_pos']==n_pos-1,['x (m)', 'y (m)']].iloc[0])
	
	for column in data:
		if column in ['n_pos', 'n_trigger', 'x (m)', 'y (m)', 'z (m)', 'n_channel', 'n_pulse']:
			continue
		for stat in STATISTICAL_QUANTITIES:
			for package in ['matplotlib', 'plotly']:
				fig = mpl.manager.new(
					title = f'{column[:column.find("(")][:-1]} {stat}',
					subtitle = f'Data set: {bureaucrat.measurement_name}',
					xlabel = 'Distance (m)',
					ylabel = column,
					package = package,
				)
				for ch in sorted(set(data['n_channel'])):
					if stat == 'mean':
						y_vals = data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).mean()[column]
					elif stat == 'std':
						y_vals = data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).std()[column]
					fig.plot(
						distance,
						y_vals,
						label = f'CH {ch}',
						marker = '.',
					)
				mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path/Path('png' if package=='matplotlib' else 'html'))
		fig = mpl.manager.new(
			title = f'{column[:column.find("(")][:-1]}',
			subtitle = f'Data set: {bureaucrat.measurement_name}',
			xlabel = 'Distance (m)',
			ylabel = column,
			package = 'plotly',
		)
		for ch in sorted(set(data['n_channel'])):
			fig.error_band(
				distance,
				y = data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).mean()[column],
				ylow = data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).mean()[column] - data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).std()[column],
				ytop = data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).mean()[column] + data.loc[data['n_channel']==ch, ['n_pos', column]].groupby(['n_pos']).std()[column],
										label = f'CH {ch}',
				marker = '.',
			)
		mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path/Path('error band plots'))
	
	fig = mpl.manager.new(
		title = f'Normalized collected charge',
		subtitle = f'Data set: {bureaucrat.measurement_name}',
		xlabel = 'Distance (m)',
		ylabel = 'Normalized collected charge',
	)
	normalized_collected_charge_df = pandas.DataFrame({'n_pos': n_poss})
	for ch in sorted(set(data['n_channel'])):
		normalized_collected_charge_df[f'channel {ch} average'] = data.loc[data['n_channel']==ch, ['n_pos','Collected charge (a.u.)']].groupby(['n_pos']).mean()
		normalized_collected_charge_df[f'channel {ch} std'] = data.loc[data['n_channel']==ch, ['n_pos','Collected charge (a.u.)']].groupby(['n_pos']).std()
		normalized_collected_charge_df[f'channel {ch} average'] -= normalized_collected_charge_df[f'channel {ch} average'].min()
		normalization_factor = normalized_collected_charge_df[f'channel {ch} average'].max()
		normalized_collected_charge_df[f'channel {ch} average'] /= normalization_factor
		normalized_collected_charge_df[f'channel {ch} std'] /= normalization_factor
		fig.error_band(
			distance,
			y = normalized_collected_charge_df[f'channel {ch} average'],
			ylow = normalized_collected_charge_df[f'channel {ch} average'] - normalized_collected_charge_df[f'channel {ch} std'],
			ytop = normalized_collected_charge_df[f'channel {ch} average'] + normalized_collected_charge_df[f'channel {ch} std'],
			label = f'CH {ch}',
			marker = '.',
		)
	
	
	for ch_A in sorted(set(data['n_channel'])):
		for ch_B in sorted(set(data['n_channel'])):
			fig = mpl.manager.new(
				title = f'Sum of channels {ch_A} and {ch_B}',
				subtitle = f'Data set: {bureaucrat.measurement_name}',
				xlabel = 'Distance (m)',
				ylabel = 'Normalized collected charge',
			)
			for ch in [ch_A,ch_B]:
				fig.error_band(
					distance,
					y = normalized_collected_charge_df[f'channel {ch} average'],
					ylow = normalized_collected_charge_df[f'channel {ch} average'] - normalized_collected_charge_df[f'channel {ch} std'],
					ytop = normalized_collected_charge_df[f'channel {ch} average'] + normalized_collected_charge_df[f'channel {ch} std'],
					label = f'CH {ch}',
					marker = '.',
				)
			summed_charge_mean = normalized_collected_charge_df[f'channel {ch_A} average'] + normalized_collected_charge_df[f'channel {ch_B} average']
			summed_charge_std = normalized_collected_charge_df[f'channel {ch_A} std'] + normalized_collected_charge_df[f'channel {ch_B} std']
			fig.error_band(
				distance,
				y = summed_charge_mean,
				ylow = summed_charge_mean - summed_charge_std,
				ytop = summed_charge_mean + summed_charge_std,
				label = f'CH {ch_A} + CH {ch_B}',
				marker = '.',
			)
	mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path/Path('error band plots'))
	
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

