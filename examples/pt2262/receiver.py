import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets, Princeton25bit_Protocol

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
cc1101.configurator.set_receiver_bandwidth_hz(101e3)

protocol = Princeton25bit_Protocol()
protocol.setup_configurator(cc1101.configurator)

cc1101.set_configuration()
cc1101.configurator.print_description()    

packets = []

for i in range(50):
    logger.info("Waiting for Packet...")
    packet = cc1101.receive(timeout_ms=10000, max_same_bits=4)
    logical_values = protocol.parse(packet.get_bitstream())
    print(len(protocol._logical_bits), protocol._logical_bits)
    if logical_values:
        logger.info(f"Address: {logical_values['address']:06x}, Data: {logical_values['data']:02x}")
        packets.append(logical_values)
    logger.info(packet)

print(len(packets))

