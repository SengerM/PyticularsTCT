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
    def __init__(self, port: str):
        if not isinstance(port, str):
            raise TypeError('<port> must be a string')
        self._dev_id = pyximc.lib.open_device(b'xi-com:\\\\.\\'+(bytes(port, 'utf8'))) # https://libximc.xisupport.com/doc-en/ximc_8h.html#a9027dc684f63de34956488bffe9e4b36
    
    def __del__(self):
        pyximc.lib.close_device(pyximc.byref(ctypes.c_int(self._dev_id)))
    
    def move_to(self, units: int):
        pyximc.lib.command_move(self._dev_id, units, 0) # https://libximc.xisupport.com/doc-en/ximc_8h.html#aa6113a42efa241396c72226bba9acd59
        pyximc.lib.command_wait_for_stop(self._dev_id, 10) # https://libximc.xisupport.com/doc-en/ximc_8h.html#ad9324f278bf9b97ad85b3411562ef0f7

if __name__ == "__main__":
    stage = Stage(port='COM5')
    for pos in [0,1000,2000,3000]:
        print(f'Moving stage to {pos}...')
        stage.move_to(pos)
    
    
