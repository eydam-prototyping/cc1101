
import logging
import epCC1101.addresses as addresses
from epCC1101.driver import Abstract_Driver
from rust_rpi_cc1101_driver import asynchronous_serial_read, asynchronous_serial_write, synchronous_serial_write
import sys
if sys.implementation.name == "cpython":
    if sys.platform == "linux":
        import RPi.GPIO as GPIO
        import pigpio
        import spidev
    if sys.platform.startswith("win"):
        from stubs import GPIO
        from stubs import pigpiod
        from stubs import spidev

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Driver(Abstract_Driver):
    chunk_size = 32
    fifo_rw_interval = 0.001
    def __init__(self, spi_bus:int=0, cs_pin:int=0, spi_speed_hz:int=55700, gdo0:int=23, gdo1:int=None, gdo2:int=None):
        logger.info(f"Initializing SPI device on bus {spi_bus}, cs_pin {cs_pin}, spi_speed_hz {spi_speed_hz}")

        self.spi_bus = spi_bus
        self.cs_pin = cs_pin
        self.spi_speed_hz = spi_speed_hz
        self.gdo0 = gdo0
        self.gdo1 = gdo1
        self.gdo2 = gdo2

        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_bus, self.cs_pin)
        self.spi.max_speed_hz = self.spi_speed_hz

        #

    def read_byte(self, register:int):
        logger.debug(f"Reading byte from address 0x{register:02X}")
        result = self.spi.xfer2([register | addresses.SPI_READ_MASK, 0])[1]
        logger.debug(f"Read byte {result}")
        return result
    
    def read_status_register(self, register):
        logger.debug(f"Reading status register 0x{register:02X}")
        result = self.spi.xfer2([register | addresses.SPI_READ_BURST_MASK, 0])[1]
        logger.debug(f"Read status register {result}")
        return result
    
    def read_burst(self, register:int, length:int):
        logger.debug(f"Reading burst from address 0x{register:02X} with length {length}")
        result = self.spi.xfer2([register | addresses.SPI_READ_BURST_MASK] + [0]*length)[1:]
        logger.debug(f"Read burst {result}")
        return result

    def command_strobe(self, register:int):
        logger.debug(f"Sending command strobe to address 0x{register:02X}")
        self.spi.xfer2([register | addresses.SPI_WRITE_MASK])

    def write_burst(self, register:int, data:bytes):
        logger.debug(f"Writing burst to address 0x{register:02X} with data {data}")
        self.spi.xfer2([register | addresses.SPI_WRITE_BURST_MASK] + data)

    def wait_for_edge(self, pin:int, edge:int, timeout:int=1000):
        if self.gdo0 is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN)
        
        result = GPIO.wait_for_edge(pin, edge, timeout=timeout)
        
        if self.gdo0 is not None:
            GPIO.cleanup()
        return result

    def read_gdo0(self):
        if self.gdo0 is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gdo0, GPIO.IN)
            result = GPIO.input(self.gdo0)
            GPIO.cleanup()
            return result
        else:
            return None
        
    def read_gdo2(self):
        if self.gdo2 is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gdo2, GPIO.IN)
            result = GPIO.input(self.gdo2)
            GPIO.cleanup()
            return result
        else:
            return None
    
    def asynchronous_serial_read(self, threshold_pin_number:int, data_pin_number:int, timeout_ms:int):
        return asynchronous_serial_read(threshold_pin_number, data_pin_number, timeout_ms)
    
    def asynchronous_serial_write(self, data_pin_number:int, baudrate:int, data):
        return asynchronous_serial_write(data_pin_number, baudrate, data)
    
    def synchronous_serial_write(self, clock_pin_number:int, data_pin_number:int, data):
        return synchronous_serial_write(clock_pin_number, data_pin_number, data)