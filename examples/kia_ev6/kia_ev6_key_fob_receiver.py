import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from cc1101 import Cc1101
from rpi_driver import Driver
import presets

driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)

cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_kia_ev6_key_fob)

# When pressing a button on the key fob, the packets have a fixed length of 24 bytes (payload).
# The signal is always send 5 times without pause. The first time, the cc1101 cuts off the first 
# 4 bytes (2 Bytes Preamble, 2 Bytes Sync Word). The following 4 times the cc1101 receives the 
# complete packet, including preamble. So if you set the length to 24 * 5 + 4 * 4 = 136, you will 
# receive all 5 packets.
cc1101.configurator.set_packet_length_mode(0)
cc1101.configurator.set_packet_length(136)

# Set the configuration
cc1101.set_configuration()

# Print the configuration
cc1101.configurator.print_description()

payload_length = 24

def get_payload(packet):
    return packet.payload[0:payload_length]

def check_payload_quality(packet):
    # check if the payload is always the same
    quality = 0
    payload = get_payload(packet)
    for i in range(1,6):
        if payload == packet.payload[i*(4+payload_length):i*(4+payload_length)+payload_length]:
            quality += 1
    return quality

def manchester_decode(payload):
    # create a binary string from the payload
    raw_binary = "".join([f"{x:08b}" for x in payload])
    raw_binary = raw_binary[1:]

    # decode manchester (01 -> 0, 10 -> 1)
    raw_binary_manchester = ""
    for i in range(0, len(raw_binary), 2):
        if raw_binary[i:i+2] == "01":
            raw_binary_manchester += "0"
        elif raw_binary[i:i+2] == "10":
            raw_binary_manchester += "1"
        else:
            pass

    decoded = bytes([int(raw_binary_manchester[i:i+8], 2) for i in range(0, len(raw_binary_manchester), 8)])
    return decoded

for i in range(5):
    logger.info("Waiting for Packet...")
    packet = cc1101.receive(timeout_ms=10000)
    logger.info("raw data: " + " ".join([f"{x:02x}" for x in packet.payload]))
    payload = get_payload(packet)
    logger.info("payload: " + " ".join([f"{x:02x}" for x in payload]))
    logger.info(f"quality: {check_payload_quality(packet)}/4") # how many times the payload is the same
    decoded = manchester_decode(payload)
    if decoded is not None:
        logger.info("decoded: " + " ".join([f"{x:02x}" for x in decoded]))
    else:
        logger.error("decoding failed")
