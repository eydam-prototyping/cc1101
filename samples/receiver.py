import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from cc1101 import Cc1101
from rpi_driver import Driver
import presets

driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_dr5k7_dev5k2_2fsk_rxbw58k_kia)
cc1101.configurator.set_data_rate_baud(5700)
cc1101.configurator.set_sync_mode(5)
cc1101.configurator.set_sync_word([0xD3, 0x4B])
cc1101.configurator.set_crc_enable(0)
cc1101.configurator.set_preamble_length_bytes(2)
cc1101.set_configuration()
print(cc1101.configurator._registers)


cc1101.configurator.print_description()
for i in range(10):
    print("Waiting for Packet...")
    packet = cc1101.receive(timeout_ms=10000)
    print(packet)
    print(" ,".join([f"0x{x:02X}" for x in packet.payload]))