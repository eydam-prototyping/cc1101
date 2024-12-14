import spidev
import logging
import epCC1101.addresses as addresses
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Driver:
    chunk_size = 32
    fifo_rw_interval = 0.01
    def __init__(self, spi_bus:int=0, cs_pin:int=0, spi_speed_hz:int=55700, gdo0:int=None):
        logger.info(f"Initializing SPI device on bus {spi_bus}, cs_pin {cs_pin}, spi_speed_hz {spi_speed_hz}")

        self.spi_bus = spi_bus
        self.cs_pin = cs_pin
        self.spi_speed_hz = spi_speed_hz
        self.gdo0 = gdo0

        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_bus, self.cs_pin)
        self.spi.max_speed_hz = self.spi_speed_hz

        if self.gdo0 is not None:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gdo0, GPIO.IN)

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
        return GPIO.wait_for_edge(pin, edge, timeout=timeout)
        
    def read_gdo0(self):
        return GPIO.input(self.gdo0)