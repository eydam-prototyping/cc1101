import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import time

from epCC1101 import Cc1101, Driver, presets

# Create a driver object
#driver = Driver(spi_bus=0, cs_pin=0, gdo0=23, gdo2=17)
driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
cc1101.configurator.set_patable([0x00, 0x80])
cc1101.configurator.set_packet_format(1)        # Set packet format to be sync serial
cc1101.configurator.set_base_frequency_hz(433.94e6)
cc1101.configurator.set_receiver_bandwidth_hz(101e3)
cc1101.configurator.set_data_rate_baud(2780)
#cc1101.configurator.set_GDOx_config(0, 0x0B)    # Set GDO0 to be High when RSSI is above threshold
#cc1101.configurator.set_GDOx_config(2, 0x0B)    # Set GDO2 to output the received data
cc1101.set_configuration()

cc1101.configurator.print_description()

def build_princeton_packet(data = [0x00, 0x00, 0x14]):
    bits = [0]*16
    for byte in data:
        for i in range(8):
            if byte & 0x80:
                bits += [1, 1, 1, 0]
            else:
                bits += [1, 0, 0, 0]
            byte <<= 1
    bits += [1, 0, 0, 0]
    bits += [0, 0, 0, 0]
    bits += [0]*16
    print(bits)
    packet = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte <<= 1
            byte |= bits[i+j]
        packet.append(byte)
    return packet


for i in range(10):
    logger.info("Waiting for Packet...")
    #cc1101.transmit([0x00]*3+[0x88]*10+[0xE8, 0xE8, 0x80, 0x00])
    packet = build_princeton_packet([0x00, 0x00, 0x10+i])
    packet = 5 * packet
    cc1101.transmit(packet)
    #packet = build_princeton_packet([0x00, 0x00, 0x14])
    print(" ".join([f"{byte:02X}" for byte in packet]))
    
    time.sleep(1)
    
