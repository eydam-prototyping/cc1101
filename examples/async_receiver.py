import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets
import epCC1101.addresses as addr
import RPi.GPIO as GPIO
import time
import serial

driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)

cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_kia_ev6_key_fob)
cc1101.configurator.set_sync_mode(0)
cc1101.configurator.set_data_rate_baud(5650)
# Set the configuration
cc1101.set_configuration()

cc1101.driver.write_burst(addr.PKTCTRL0, [0x32])  # Async, no CRC
cc1101.driver.write_burst(addr.PKTCTRL1, [0x04]) 
cc1101.driver.write_burst(addr.IOCFG0, [0x0E]) 
cc1101.driver.write_burst(addr.IOCFG2, [0x0D]) 
cc1101.driver.write_burst(addr.AGCTRL0, [0x91])
cc1101.driver.write_burst(addr.AGCTRL1, [0x40])
cc1101.driver.write_burst(addr.AGCTRL2, [0x07]) 

cc1101.get_configuration()

# Print the configuration
cc1101.configurator.print_description()

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#GPIO.setup(18, GPIO.IN)
GPIO.setup(27, GPIO.OUT)

ser = serial.Serial(
            port="/dev/ttyS0",
            baudrate=cc1101.configurator.get_data_rate_baud(),
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE_POINT_FIVE,
            timeout=10
        )

logger.info("Waiting for Packet...")
packet = cc1101.set_receive_mode()
for i in range(100):
    #while cc1101.get_rssi_dbm() < -80:
    #    time.sleep(0.0001)
    #dt = 1/(cc1101.configurator.get_data_rate_baud()*3)
    GPIO.wait_for_edge(cc1101.driver.gdo0, GPIO.RISING)
    ser.reset_input_buffer()
    time.sleep(0.05)
    data = b''
    while GPIO.input(cc1101.driver.gdo0):
        data += ser.read(ser.in_waiting)
        time.sleep(0.005)
        
    data += ser.read(ser.in_waiting)
    #dt = 0.00017
    #print(f"dt = {dt*1000:2f}ms")
    #print(f"baud = {cc1101.configurator.get_data_rate_baud()}")
    #GPIO.output(27, GPIO.HIGH)
    #last = time.time()
    #data = []
    #for i in range(200):
        #x = GPIO.wait_for_edge(17, GPIO.BOTH, timeout=100000)
        #y = GPIO.input(17)
        #print(f"{y}\t{i:03d}")#, f"{(time.time()-last)*1000:02.2f} ms", f"rssi: {cc1101.get_rssi_dbm()} dBm")
        #data += [y]
        #time.sleep(dt)
        #last = time.time()
    #print(f"delta = {time.time()-last}")
    #GPIO.output(27, GPIO.LOW)
    print(len(data))
    print(" ".join([f"{x:02x}" for x in data]))
    print("".join([f"{x:08b}" for x in data[0:10]]))
    time.sleep(1)