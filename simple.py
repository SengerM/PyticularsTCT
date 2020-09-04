import os
import sys
import time
from ctypes import *

if sys.version_info >= (3,0):
    import urllib.parse

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)

if sys.platform in ("win32", "win64"):
    libdir = os.path.join(ximc_dir, sys.platform)
    os.environ["Path"] = libdir + ";" + os.environ["Path"]

try: 
    from pyximc import *
    from pyximc import MicrostepMode
except ImportError as err:
    print ('Can not import pyximc module.')
    exit()
except OSError as err:
    print ('Can not load libximc library.')
    exit()

 # All windows in attenuator wheels are marked:
 #     Wheel_1              Wheel_2
 #      "1": 0               "1": 0
 #      "0": 1               "0": 1
 #    "0.9": 2             "0.8": 2
 #    "0.5": 3             "0.3": 3
 #    "0.1": 4            "0.03": 4
 #   "0.01": 5           "0.003": 5
 #  "0.001": 6          "0.0003": 6
 # "0.0001": 7         "0.00003": 7

""" standart ".cfg" file, which can be downloaded to device using XILab,
    overloads command_homezero command, suitable for us """

""" Complicated variant with transition to user units """
def set_pos_calb(device_id, pos_wheel1, pos_wheel2):
	calb = calibration_t()
	calb.A = c_double(0.04)             # 1 переход = 25 шагов
	calb.MicrostepMode = 1                 # режим без разделения на микрошаги
	lib.command_wait_for_stop(att_id, 10)  # задержка, чтобы команды не перекрывались
	lib.command_move_calb(att_id, c_float(pos_wheel2), byref(calb))
	lib.command_wait_for_stop(att_id, 10)
	if pos_wheel1 > pos_wheel2:            # иначе колесо-1 будет цеплять колесо-2
		pos_wheel1 = pos_wheel1 - 8
	lib.command_move_calb(att_id, c_float(pos_wheel1), byref(calb))

""" or we can just multiply by 25 """
def set_pos(device_id, pos_wheel1, pos_wheel2):
    lib.command_wait_for_stop(att_id, 10)
    lib.command_move(att_id, 25*pos_wheel2, 0)
    lib.command_wait_for_stop(att_id, 10)
    if pos_wheel1 > pos_wheel2:
        pos_wheel1 = pos_wheel1 - 8
    lib.command_move(att_id, 25*pos_wheel1, 0)


if __name__ == "__main__":
    att_id = lib.open_device(b'xi-com:\\\\.\\'+(bytes(sys.argv[1], 'utf8')))
    print("ID: ", att_id)
    lib.command_homezero(att_id)
    print("Calibration...")
    lib.command_wait_for_stop(att_id, 10)
    print("First window number: ")
    wnd1 = input()
    if wnd1 == "exit":
        c_id = c_int(att_id)
        lib.close_device(byref(c_id))
        sys.exit()
    print("Second window number: ")
    wnd2 = input()
    set_pos_calb(att_id, int(wnd1), int(wnd2))
    lib.command_wait_for_stop(att_id)
