import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets
import epCC1101.addresses as addr
from epCC1101.raw_packet_interpreter import Interpreted_Packet

driver = Driver(spi_bus=0, cs_pin=0, gdo0=23, gdo2=17)

cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_dr5k7_dev5k2_2fsk_rxbw58k)
cc1101.configurator.set_packet_length_mode(2)
cc1101.set_configuration()
cc1101.driver.write_burst(addr.PKTCTRL0, [0x32])  # Async, no CRC
cc1101.driver.write_burst(addr.PKTCTRL1, [0x04]) 
cc1101.driver.write_burst(addr.IOCFG0, [0x0E]) 
cc1101.driver.write_burst(addr.IOCFG2, [0x0D]) 
cc1101.driver.write_burst(addr.AGCTRL0, [0x91])
cc1101.driver.write_burst(addr.AGCTRL1, [0x40])
cc1101.driver.write_burst(addr.AGCTRL2, [0x07]) 
cc1101.get_configuration()

cc1101.configurator.print_description()

packet = cc1101.receive(10000)
#print(packet)
print(packet.edges)
print(packet.get_bitstream())