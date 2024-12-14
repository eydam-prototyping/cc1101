import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from cc1101 import Cc1101
from rpi_driver import Driver
import presets
import time

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=1, gdo0=24)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_sample_1)
cc1101.configurator.set_modulation_format(3)
cc1101.configurator.set_base_frequency_hz(433.92e6)
#cc1101.configurator.set_sync_word([0xff, 0x55])
cc1101.configurator.set_data_rate_baud(2800)
cc1101.configurator.set_patable([0, 0x0E])
cc1101.configurator.set_sync_mode(5)
cc1101.configurator.set_packet_length_mode(0)
cc1101.configurator.set_packet_length(12)
cc1101.configurator.set_receiver_bandwidth_hz(101e3)
cc1101.set_configuration()

cc1101.configurator.print_description()

for i in range(5):
    logger.info("Sending packet...")
    cc1101.transmit(bytes([0x11 for x in range(10)]+[0x1D, 0x1D]))
    time.sleep(1)