from epCC1101 import Cc1101, Driver, presets
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import csv
import datetime

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

# Load a preset configuration
cc1101.load_preset(presets.rf_setting_dr5k7_dev5k2_2fsk_rxbw58k)

# Change the preset as you like
# Set the data rate to 5700 baud
cc1101.configurator.set_data_rate_baud(5700)
# Set the sync mode to 5 = 15/16 + carrier-sense above threshold
cc1101.configurator.set_sync_mode(5)
# Set the sync word to 0xD34B
cc1101.configurator.set_sync_word([0xD3, 0x4B])
# Disable CRC
cc1101.configurator.set_crc_enable(0)
# Set the preamble length to 2 bytes
cc1101.configurator.set_preamble_length_bytes(2)
# Set the receiver bandwidth to 101 kHz
cc1101.configurator.set_receiver_bandwidth_hz(101e3)
# Set the packet length mode to 1 = variable
cc1101.configurator.set_packet_length_mode(1)
# Set the configuration
cc1101.set_configuration()

# Print the configuration
cc1101.configurator.print_description()

max_packets = 5
packet_timeout_ms = 10000

with open('received_packets.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Timestamp','RSSI', 'LQI', 'CRC_OK', 'Payload'])

    for i in range(max_packets):
        logger.info("Waiting for Packet...")
        packet = cc1101.receive(timeout_ms=packet_timeout_ms)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(packet)
        logger.info(" ".join([f"{x:02x}" for x in packet.payload]))
        csvwriter.writerow([timestamp, packet.rssi, packet.lqi, packet.crc_ok, packet.payload])
        csvfile.flush()