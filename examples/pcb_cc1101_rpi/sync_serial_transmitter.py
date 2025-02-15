import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import time

from epCC1101 import Cc1101, Driver, presets, SyncTxPacket

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=1, gdo0=22, gdo2=23)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
cc1101.configurator.set_packet_format(1)        # Set packet format to be sync serial

cc1101.configurator.set_data_rate_baud(1400)
#cc1101.configurator.set_patable([0x00, 0x10])
cc1101.configurator.set_patable([0x00, 0x40])
cc1101.set_configuration()

cc1101.configurator.print_description()

for i in range(5):
    logger.info("Transmitting...")
    packet = SyncTxPacket(payload=[i for i in range(1, 10)])
    cc1101.transmit(packet)
    time.sleep(1)