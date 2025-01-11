import sys

from .cc1101 import Cc1101

if sys.implementation.name == "micropython":
    raise NotImplementedError("This library is not compatible with MicroPython")
elif sys.implementation.name == "cpython":
    if sys.platform == "linux":
        from .rpi_driver import Driver
    if sys.platform.startswith("win"):
        from .stubs.driver import Driver