# This was adapted from https://github.com/Negrebetskiy/Attenuator

import os
import sys
import time
import ctypes

if sys.version_info >= (3,0):
    import urllib.parse

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)

if sys.platform in ("win32", "win64"):
    libdir = os.path.join(ximc_dir, sys.platform)
    os.environ["Path"] = libdir + ";" + os.environ["Path"]

import pyximc

class Stage:
    """
    https://libximc.xisupport.com/doc-en/ximc_8h.html#affd3ae9915d9a352d28f0c2c6872753d
    """
    def __init__(self, port: str):
        if not isinstance(port, str):
            raise TypeError('<port> must be a string')
        self._dev_id = pyximc.lib.open_device(b'xi-com:\\\\.\\'+(bytes(port, 'utf8'))) # https://libximc.xisupport.com/doc-en/ximc_8h.html#a9027dc684f63de34956488bffe9e4b36
    
    def __del__(self):
        pyximc.lib.close_device(ctypes.byref(ctypes.c_int(self._dev_id)))
    
    @property
    def serial_number(self):
        serial_number = ctypes.c_uint(100)
        pyximc.lib.get_serial_number(self._dev_id, ctypes.byref(serial_number))
        return serial_number.value
    
    @property
    def information(self):
        info = pyximc.device_information_t()
        pyximc.lib.get_device_information(self._dev_id, ctypes.byref(info))
        return {
            "Manufacturer": info.Manufacturer.decode("utf-8"),
            "ManufacturerId": info.ManufacturerId.decode("utf-8"),
            "ProductDescription": info.ProductDescription.decode("utf-8"),
            "Major": info.Major,
            "Minor": info.Minor,
            "Release": info.Release,
        }
    
    def reset_position(self):
        pyximc.lib.command_homezero(self._dev_id)
    
    def move_to(self, units: int):
        if not isinstance(units, int):
            raise TypeError('<units> must be an int')
        pyximc.lib.command_move(self._dev_id, units, 0) # https://libximc.xisupport.com/doc-en/ximc_8h.html#aa6113a42efa241396c72226bba9acd59
        pyximc.lib.command_wait_for_stop(self._dev_id, 10) # https://libximc.xisupport.com/doc-en/ximc_8h.html#ad9324f278bf9b97ad85b3411562ef0f7
    
    def move_rel(self, units: int):
        if not isinstance(units, int):
            raise TypeError('<units> must be an int')
        pyximc.lib.command_movr(self._dev_id, units, 0)
        pyximc.lib.command_wait_for_stop(self._dev_id, 10)
    
    def get_position(self):
        pos = pyximc.get_position_t()
        pyximc.lib.get_position(self._dev_id, ctypes.byref(pos))
        return {'Position': pos.Position, 'uPosition': pos.uPosition, 'EncPosition': pos.EncPosition}

if __name__ == "__main__":
    stages = []
    for port in ['COM3', 'COM4', 'COM5']:
        stages.append(Stage(port))
    X = stages[0]
    Y = stages[1]
    Z = stages[2]
    for stage in stages:
        print(stage.serial_number)
        print(stage.information)
    
    # stage.reset_position()
    while True:
        print(Z.get_position())
        pos = int(input('Enter new position: '))
        print(f'Moving stage to {pos}...')
        Z.move_to(pos)

    
