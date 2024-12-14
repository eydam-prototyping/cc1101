import sys

from .cc1101 import Cc1101


if sys.implementation.name == "micropython":
    raise NotImplementedError("This library is not compatible with MicroPython")
    
if sys.implementation.name == "cpython":
    from epCC1101.rpi_driver import Driver