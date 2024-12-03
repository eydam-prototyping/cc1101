import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import time
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from cc1101 import Cc1101
from rpi_driver import Driver
import addresses

driver = Driver(spi_bus=0, cs_pin=1, gdo0=24)
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.configurator._registers = [      0x29,      0x2E,      0x06,      0x07,      0xD3,      0x91,      0xFF,      0x04,      0x05,      0x00,      0x00,      0x06,      0x00,      0x10,      0xB0,      0x71,      0xF7,      0xC4,      0x03,      0x22,      0xF8,      0x42,      0x07,      0x30,      0x18,      0x36,      0x6C,      0x03,      0x40,      0x91,      0x87,      0x6B,      0xF8,      0x56,      0x10,      0xE9,      0x2A,      0x00,      0x1F,      0x41,      0x00,      0x59,      0x7F,      0x3F,      0x81,      0x35,      0x09]
cc1101.set_configuration()
cc1101.driver.write_burst(addresses.PATABLE, [0x8E])

cc1101.configurator.print_description()
for i in range(15):
    print("Transmitting...")
    cc1101.transmit(b"Hello, world!" + bytes([i]))
    time.sleep(1)