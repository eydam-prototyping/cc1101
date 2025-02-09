import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from epCC1101 import Cc1101, Driver, presets

# Create a driver object
driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)

# Create a CC1101 object
cc1101 = Cc1101(driver=driver)
cc1101.reset()

cc1101.load_preset(presets.rf_setting_async_ask_ook)
cc1101.configurator.set_packet_format(1)        # Set packet format to be sync serial
cc1101.configurator.set_base_frequency_hz(433.94e6)
cc1101.configurator.set_receiver_bandwidth_hz(101e3)
cc1101.configurator.set_data_rate_baud(2780)
cc1101.configurator.set_GDOx_config(0, 0x0B)    # Set GDO0 to be High when RSSI is above threshold
cc1101.configurator.set_GDOx_config(2, 0x0C)    # Set GDO2 to output the received data
cc1101.set_configuration()

cc1101.configurator.print_description()

class PrincetonPacket:
    def __init__(self, physical_bits):
        self.physical_bits = physical_bits
        self.logical_bits = []
        self.bytes = []
        if self.try_parse_bits():
            if self.try_parse_bytes():
                logger.info("Packet parsed successfully.")
            else:
                logger.error("Failed to parse bytes.")
        else:
            logger.error("Failed to parse bits.")
    
    def try_parse_bits(self):
        """Try to parse the physical bits into logical bits.

        Returns:
            Boolean: True, if 25 logical bits are parsed successfully.
        """
        self.logical_bits = []

        # Remove leading zeros
        while self.physical_bits[0] == 0:
            self.physical_bits.pop(0)
            if len(self.physical_bits) == 0:
                return False
        
        for i in range(len(self.physical_bits)//4):
            if self.physical_bits[i*4:i*4+4] == [1, 0, 0, 0]:
                self.logical_bits.append(0)
            elif self.physical_bits[i*4:i*4+4] == [1, 1, 1, 0]:
                self.logical_bits.append(1)
            elif self.physical_bits[i*4:i*4+4] == [0, 0, 0, 0]:
                break

        print(self.logical_bits)
        # Successful parsing if between 22 and 25 bits are parsed and the last bit is 0 (sync bit)
        if (25 >= len(self.logical_bits) >= 22) and (self.logical_bits[-1] == 0):
            # if less than 25 bits where found, assume leading zeros
            while len(self.logical_bits) < 25:
                self.logical_bits.insert(0, 0)
            return True
        
        return False
    
    def try_parse_bytes(self):
        """Try to parse the logical bits into bytes.

        Returns:
            Boolean: True, if 3 bytes are parsed successfully.
        """
        self.bytes = []
        for i in range(len(self.logical_bits)//8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | self.logical_bits[i*8+j]
            self.bytes.append(byte)
        
        if len(self.bytes) == 3:
            return True
        
        return False

    def __str__(self):
        return "PrincetonPacket(" + " ".join([f"0x{x:02x}" for x in self.bytes]) + ")"

for i in range(10):
    logger.info("Waiting for Packet...")
    packet = cc1101.receive(timeout_ms=10000)
    logger.info([int(x) for x in packet.bits])
    princeton_packet = PrincetonPacket([int(x) for x in packet.bits])
    logger.info(princeton_packet)

