# Motors controller

This "ximc" stuff is to control the motors in the TCT setup. It is a binary library provided by the manufacturer (?) of the motors. The binaries are different for each operating system, fortunately they provide for many systems. But it is not trivial to load them from Python such that they work. So in this directory I collected some of the binaries (Linux and Windows) and added a modified version of `pyximc.py` such that it becomes easy to make it work.

The latest version of this library can be found [here](https://doc.xisupport.com/en/8smc5-usb/8SMCn-USB/Programming/Programming_guide.html), more specifically [here](http://files.xisupport.com/Software.en.html#development-kit). What I did is to download [this file](http://files.xisupport.com/libximc/libximc-2.13.3-all.tar.gz) and copy-pasted the Windows and Linux binaries here (see `win64` and `debian-amd64` directories). 

In [this link](https://libximc.xisupport.com/doc-en/index.html) there is documentation about *libximc*.
