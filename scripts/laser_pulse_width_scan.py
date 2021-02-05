from PyticularsTCT.oscilloscope import LecroyWR640Zi # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.tct_setup import TCTStages # https://github.com/SengerM/PyticularsTCT
from PyticularsTCT.particulars_laser_control import ParticularsLaserControl
import numpy as np
from time import sleep
import myplotlib as mpl
from lgadtools.LGADSignal import LGADSignal # https://github.com/SengerM/lgadtools
from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramProgressBar # https://github.com/SengerM/data_processing_bureaucrat
from pathlib import Path

CHANNELS = ['CH1']

def script_core(
	measurement_name: str, 
	laser_pulse_widths: tuple, 
	n_triggers: int = 1,
):
	bureaucrat = Bureaucrat(
		str(Path(f'C:/Users/tct_cms/Desktop/TCT_measurements_data/{measurement_name}')),
		variables = locals(),
		new_measurement = True,
	)
	
	osc = LecroyWR640Zi('USB0::0x05FF::0x1023::4751N40408::INSTR')
	laser = ParticularsLaserControl()

	ofile_path = bureaucrat.processed_data_dir_path/Path('measured_data.csv')
	with open(ofile_path, 'w') as ofile:
		print(f'n_pulse_width\tn_trigger\tLaser pulse width (%)\tn_channel\tAmplitude (V)\tNoise (V)\tRise time (s)\tCollected charge (a.u.)\tt_10 (s)\tt_50 (s)\tt_90 (s)\tTime over 20 % threshold (s)', file = ofile)
	
	with TelegramProgressBar(len(laser_pulse_widths)*n_triggers, bureaucrat) as progress_bar:
		n_pulse_width = -1
		for laser_pulse_width in laser_pulse_widths:
			n_pulse_width += 1
			laser.pulse_width = laser_pulse_width
			laser.status = 'on'
			sleep(0.1)
			for n_trigger in range(n_triggers):
				progress_bar.update(1)
				n_attempts = 0
				success = [False]*len(CHANNELS)
				while not all(success) and n_attempts < 5:
					n_attempts += 1
					raw_data = osc.acquire_one_pulse()
					success = [False]*len(CHANNELS)
					signals = {}
					for ch in CHANNELS:
						signals[ch] = LGADSignal(
							time = raw_data[ch]['time'],
							samples = -1*raw_data[ch]['volt'],
						)
					for idx,ch in enumerate(CHANNELS):
						s = signals[ch]
						try: # Try to calculate all the quantities of interest.
							s.amplitude
							s.noise
							s.risetime
							s.collected_charge()
							s.time_at(10)
							s.time_at(50)
							s.time_at(90)
							s.time_over_threshold(20)
						except Exception as exception:
							print(f'Unable to parse at n_pulse_width = {n_pulse_width} for {ch}, trigger number {n_trigger}, I will try {5-n_attempts} times more.')
							fig = mpl.manager.new(
								title = f'Unable to parse n_pulse_width={n_pulse_width} {ch} n_trigger={n_trigger}',
								subtitle = bureaucrat.measurement_name,
								xlabel = 'Time (s)',
								ylabel = 'Amplitude (V)',
								package = 'matplotlib',
							)
							fig.plot(
								raw_data[ch]['time'],
								raw_data[ch]['volt'],
							)
							mpl.manager.save_all(mkdir = bureaucrat.processed_data_dir_path/Path('unable to process plots'))
							break
						else:
							success[idx] = True
				if not all(success): 
					print(f'Unable to save data at n_pulse_width = {n_pulse_width}, trigger number {n_trigger}. I will skip this point.')
					continue
				# If we are here it is because the data from all the triggers is good:
				for idx,ch in enumerate(CHANNELS):
					s = signals[ch]
					with open(ofile_path, 'a') as ofile:
						print(f'{n_pulse_width}\t{n_trigger}\t{laser_pulse_width}\t{idx+1}\t{s.amplitude:.6e}\t{s.noise:.6e}\t{s.risetime:.6e}\t{s.collected_charge():.6e}\t{s.time_at(10):.6e}\t{s.time_at(50):.6e}\t{s.time_at(90):.6e}\t{s.time_over_threshold(20):.6e}', file = ofile)
					if np.random.rand() < 20/len(laser_pulse_widths)/n_triggers/len(CHANNELS):
						fig = mpl.manager.new(
							title = f'Signal at n_pulse_width={n_pulse_width:05d}  n_trigg={n_trigger} {ch}',
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
	
	script_core(
		measurement_name = input('Measurement name? ').replace(' ', '_'),
		laser_pulse_widths = [(665-i)/10 for i in range(16)], 
		n_triggers = 4444,
	)
