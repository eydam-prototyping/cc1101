import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets
driver = Driver(spi_bus=0, cs_pin=0, gdo0=23, gdo2=17)

cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_dr5k7_dev5k2_2fsk_rxbw58k)
cc1101.configurator.set_packet_length_mode(2)   # Infinite packet length
cc1101.configurator.set_packet_format(3)        # Asynchronous serial mode
cc1101.configurator.set_GDOx_config(0, 0x0E)    # Set GDO0 to be High when RSSI is above threshold
cc1101.configurator.set_GDOx_config(2, 0x0D)    # Set GDO2 to output the received data
cc1101.configurator.set_agc_magn_target(7)      
cc1101.set_configuration()

cc1101.configurator.print_description()

packet = cc1101.receive(10000)
print(packet.edges)
print(packet.get_bitstream())