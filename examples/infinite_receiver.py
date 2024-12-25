import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets
import epCC1101.addresses as addr
import RPi.GPIO as GPIO
import time
import csv

driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)

cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_kia_ev6_key_fob)
cc1101.configurator.set_packet_length_mode(2)
cc1101.configurator.set_sync_word([0xaa, 0xaa])
# Set the configuration
cc1101.set_configuration()

cc1101.driver.write_burst(addr.IOCFG0, [0x0E]) 
cc1101.driver.write_burst(addr.AGCTRL0, [0x91])
cc1101.driver.write_burst(addr.AGCTRL1, [0x40])
cc1101.driver.write_burst(addr.AGCTRL2, [0x07]) 

cc1101.get_configuration()

cc1101.configurator.print_description()

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

with open(f'infinite-receive_{timestamp}.csv', mode='w') as data_file:
    data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    data_writer.writerow(["Timestamp", "RSSI", "Data"])

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
cc1101.set_receive_mode()
for i in range(100):
    GPIO.wait_for_edge(cc1101.driver.gdo0, GPIO.RISING)

    while GPIO.input(cc1101.driver.gdo0):
        data = []
        rssi = cc1101.get_rssi_dbm()
        while (cc1101.driver.read_gdo0() == GPIO.HIGH):
            trunc = cc1101.driver.read_burst(addr.RXFIFO, cc1101.driver.read_status_register(addr.RXBYTES)-1)
            if trunc is not None:
                data += trunc
            #time.sleep(0.01)
        trunc = cc1101.driver.read_burst(addr.RXFIFO, cc1101.driver.read_status_register(addr.RXBYTES))
        data += trunc

    cc1101.set_idle_mode()
    cc1101.flush_rx_fifo()
    cc1101.set_receive_mode()
    print(f"RSSI: {rssi}")
    print(" ".join([f"{byte:02X}" for byte in data]))
    with open(f'infinite-receive_{timestamp}.csv', mode='a') as data_file:
        data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), rssi,  " ".join([f"{byte:02X}" for byte in data])])