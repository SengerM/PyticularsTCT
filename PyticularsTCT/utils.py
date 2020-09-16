import numpy as np

def save_4ch_trigger(fname: str, position: tuple, data: dict):
    with open(fname, 'w') as ofile:
        print('# x_position = ' + str(position[0]), file=ofile)
        print('# y_position = ' + str(position[1]), file=ofile)
        print('# z_position = ' + str(position[2]), file=ofile)
        print('# Time (s)\tCH1 (V)\tCH2 (V)\tCH3 (V)\tCH4 (V)', file=ofile)
        for t,ch1,ch2,ch3,ch4 in zip(data['CH1']['time'],data['CH1']['volt'],data['CH2']['volt'],data['CH3']['volt'],data['CH4']['volt']):
            print(f'{t}\t{ch1}\t{ch2}\t{ch3}\t{ch4}', file=ofile)

def read_4ch_trigger(fname: str):
    with open(fname, 'r') as ifile:
        for line in ifile:
            if line[0] != '#':
                continue
            if 'x_position' in line:
                x_position = float(line.split(' ')[-1])
            if 'y_position' in line:
                y_position = float(line.split(' ')[-1])
            if 'z_position' in line:
                z_position = float(line.split(' ')[-1])
    data = np.genfromtxt(fname).transpose()
    times = data[0]
    ch1 = data[1]
    ch2 = data[2]
    ch3 = data[3]
    ch4 = data[4]
    return {
        'position': (x_position, y_position, z_position),
        'CH1': {'time': times, 'volt': ch1},
        'CH2': {'time': times, 'volt': ch2},
        'CH3': {'time': times, 'volt': ch3},
        'CH4': {'time': times, 'volt': ch4},
    }
    