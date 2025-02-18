import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import time

from epCC1101 import Cc1101, Driver, presets, SyncTxPacket, Princeton25bit_Protocol

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=1, gdo0=22, gdo2=23)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
protocol = Princeton25bit_Protocol()
protocol.setup_configurator(cc1101.configurator)

#cc1101.configurator.set_patable([0x00, 0x40])
cc1101.set_configuration()

cc1101.configurator.print_description()

for i in range(20):
    logger.info("Transmitting...")
    bits = protocol._get_physical_bits({"address":0x1234, "data":i})
    print(bits)
    payload=protocol.get_physical_bytes({"address":0x1234, "data":i})
    print(payload)
    packet = SyncTxPacket([0x00]*3 + payload + [0x00]*3)
    for _ in range(5):
        time.sleep(0.05)
        cc1101.transmit(packet)
    time.sleep(1)