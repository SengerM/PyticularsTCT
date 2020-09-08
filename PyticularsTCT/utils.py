def save_4ch_trigger(fname: str, position: tuple, data: dict):
    with open(fname, 'w') as ofile:
        print('# x_position = ' + str(position[0]), file=ofile)
        print('# y_position = ' + str(position[1]), file=ofile)
        print('# z_position = ' + str(position[2]), file=ofile)
        print('# Time (s)\tCH1 (V)\tCH2 (V)\tCH3 (V)\tCH4 (V)', file=ofile)
        for t,ch1,ch2,ch3,ch4 in zip(data['CH1']['time'],data['CH1']['volt'],data['CH2']['volt'],data['CH3']['volt'],data['CH4']['volt']):
            print(f'{t}\t{ch1}\t{ch2}\t{ch3}\t{ch4}', file=ofile)