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
import presets

driver = Driver(spi_bus=0, cs_pin=1, gdo0=24)
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_dr5k_dev5k2_2fsk_rxbw58k_kia)
cc1101.driver.write_burst(addresses.PATABLE, [0x8E])

cc1101.configurator.print_description()
for i in range(15):
    print("Transmitting...")
    cc1101.transmit(b"Hello, world!" + bytes([i]))
    time.sleep(1)