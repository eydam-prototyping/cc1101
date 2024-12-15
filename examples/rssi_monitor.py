from epCC1101 import Cc1101, Driver, presets
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import time

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

# Load a preset configuration
cc1101.load_preset(presets.rf_setting_dr5k7_dev5k2_2fsk_rxbw58k)

# Set the sync word to something other than your transmitter, beacuse 
# otherwise the cc1101 will process the packet and leave RX state
cc1101.configurator.set_sync_word([0x00, 0x00])
cc1101.set_configuration()

# Set the device to receive mode
cc1101.set_receive_mode()

# All time max RSSI
max_rssi = -120

# Update interval
update_interval = 0.3

while True:
    # max RSSI in one interval
    max_rssi_interval = -120

    # mean RSSI in one interval
    mean_rssi_interval = 0

    for i in range(10):
        rssi_dbm = cc1101.get_rssi_dbm()
        max_rssi_interval = max(max_rssi_interval, rssi_dbm)
        time.sleep(update_interval/10)

    max_rssi = max(max_rssi, max_rssi_interval)    

    print(f"RSSI: {max_rssi_interval:>7} dBm (max: {max_rssi:>7} dBm): {'|'*int((max_rssi_interval+120)/2):<50}", end="\r")
