import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
cc1101.configurator.set_data_rate_baud(2800)
cc1101.configurator.set_packet_format(3)        # Set packet format to be async serial
cc1101.set_configuration()

cc1101.configurator.print_description()

for i in range(5):
    logger.info("Waiting for Packet...")
    packet = cc1101.receive(timeout_ms=10000)
    logger.info(packet)