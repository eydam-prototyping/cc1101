import epCC1101.addresses as addresses
from epCC1101.configurator import Cc1101Configurator
import logging
import RPi.GPIO as GPIO
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Received_Packet:
    def __init__(self, payload:bytes, length:int, rssi:int, lqi:int=None, crc_ok:bool=None):
        self.payload = payload
        self.length = length
        self.rssi = rssi
        self.lqi = lqi
        self.crc_ok = crc_ok

    def __str__(self): 
        return f"Received_Packet(payload={self.payload}, length={self.length}, rssi={self.rssi}, lqi={self.lqi}, crc_ok={self.crc_ok})"

class Cc1101:
    def __init__(self, driver):
        """Initialize a CC1101 device.
        This method initializes the CC1101 radio device by resetting it and verifying
        its part number and version. It sets up communication with the device and loads
        the configuration.
        Args:
            driver: The driver object that handles low-level communication with the CC1101 device.
        Raises:
            Warning: If the chip's part number is not 0x00 or version is not 0x04/0x14,
                    a warning is logged but operation continues.
        Example:
            >>> from cc1101 import Cc1101
            >>> from rpi_driver import Driver
            >>> driver = Driver(spi_bus=0, cs_pin=0, gdo0=23)
            >>> cc1101 = Cc1101(driver)
        """
        logger.info("Initializing CC1101 device")
        self.driver = driver
        self.reset()

        partnum = self.get_chip_partnum()
        if partnum != 0x00:
            logger.warning(f"Unexpected chip partnum: 0x{partnum:02X}")
        
        version = self.get_chip_version()
        if version not in [0x04, 0x14]:
            logger.warning(f"Unexpected chip version: 0x{version:02X}")

        self.configurator = Cc1101Configurator()
        self.get_configuration()
    
    def reset(self):
        """Reset the CC1101 device.

        Performs a reset of the CC1101 radio module by sending the SRES command strobe.
        This resets all configuration registers to their default values.

        Returns:
            None
        """
        logger.debug("Resetting CC1101 device")
        self.driver.command_strobe(addresses.SRES)

    def get_chip_partnum(self):
        """
        Reads and returns the chip part number from the CC1101 device.
        The part number is read from the PARTNUM status register, which contains
        a factory-programmed identification number for the device.
        Returns:
            int: The chip part number as an 8-bit integer value.
                For CC1101, this should typically return 0x00.
        Example:
            >>> partnum = cc1101.get_chip_partnum()
            >>> print(f"Chip part number: 0x{partnum:02X}")
        """
        logger.debug("Reading chip partnum")
        partnum = self.driver.read_status_register(addresses.PARTNUM)
        logger.debug(f"Chip partnum: 0x{partnum:02X}")
        return partnum
    
    def get_chip_version(self):
        """Read the chip version from the CC1101 device.

        This method reads the version register of the CC1101 chip using the status register
        VERSION. The version is returned as a single byte value.

        Returns:
            int: The chip version as a hexadecimal value (e.g. 0x14 for version 1.4)

        Example:
            >>> version = cc1101.get_chip_version()
            >>> print(f"Chip version: 0x{version:02X}")
            Chip version: 0x14
        """
        logger.debug("Reading chip version")
        version = self.driver.read_status_register(addresses.VERSION)
        logger.debug(f"Chip version: 0x{version:02X}")
        return version
    
    def get_rssi_raw(self):
        """Reads raw RSSI (Received Signal Strength Indicator) value from the CC1101 chip.

        The device must be in RX or RX_END state to get a valid RSSI reading.

        Returns:
            int: Raw RSSI value from the RSSI status register

        Raises:
            ValueError: If device is not in RX (0x0D) or RX_END (0x0E) state

        Example:
            >>> cc1101.set_receive_mode()
            >>> rssi = cc1101.get_rssi_raw()
            >>> print(f"Raw RSSI value: {rssi}")
            Raw RSSI value: 100

        Note:
            This returns the raw register value. For the normalized RSSI in dBm, 
            use get_rssi_dbm() instead.
        """
        logger.debug("Reading raw RSSI value")
        if self.get_marc_state() not in [addresses.MARCSTATE_RX, addresses.MARCSTATE_RX_END]:
            logger.error(f"Device must be in state RX(0x0D) or RX_END(0x0E) before reading RSSI. Current state: 0x{self.get_marc_state():02X}")
            raise ValueError(f"Device must be in state RX(0x0D) or RX_END(0x0E) before reading RSSI. Current state: 0x{self.get_marc_state():02X}")
        return self.driver.read_status_register(addresses.RSSI)
    
    def get_rssi_dbm(self):
        """
        Convert raw RSSI value to dBm.

        The CC1101 RSSI value is represented in 2's complement format.
        For converting the RSSI reading to absolute power level in dBm,
        the following formulas are used:

        - If RSSI_raw >= 128:
            Power_dBm = (RSSI_raw - 256) / 2 - RSSI_offset
        - If RSSI_raw < 128:
            Power_dBm = RSSI_raw / 2 - RSSI_offset

        Where RSSI_offset is 74. (see Data Sheet)

        Returns:
            float: RSSI value in dBm

        Example:
            >>> cc1101.set_receive_mode()
            >>> rssi_dbm = cc1101.get_rssi_dbm()
            >>> print(f"RSSI in dBm: {rssi_dbm}")
            RSSI in dBm: -76.0
        """
        rssi_raw = self.get_rssi_raw()
        rssi_offset = 74
        if rssi_raw >= 128:
            return (rssi_raw - 256) / 2 - rssi_offset
        else:
            return rssi_raw / 2 - rssi_offset

    def get_configuration(self):
        """Read the configuration from the CC1101 device.
        Reads a burst of 47 configuration registers starting from IOCFG2 and the 8-byte PATABLE.
        Updates the internal configurator state with the read values.
        Returns:
            tuple: A tuple containing:
                - registers (bytes): 47 configuration register values
                - patable (bytes): 8-byte power table values
        """
        logger.debug("Reading configuration from device")
        registers = self.driver.read_burst(addresses.IOCFG2, 47)
        patable = self.driver.read_burst(addresses.PATABLE, 8)
        self.configurator._registers = registers
        self.configurator._patable = patable
        return registers, patable
    
    def set_configuration(self):
        """
        Writes the current configuration to the CC1101 device.

        This method performs two operations:
        1. Writes the configuration registers using burst mode
        2. Writes the PA (Power Amplifier) table using burst mode

        The configuration values are taken from the internal configurator object 
        which holds the register values and PA table settings.

        No parameters are required as it uses the internal configuration state.

        Returns:
            None

        Example:
            >>> cc1101.configurator.set_data_rate_baud(9600)
            >>> cc1101.set_configuration()
        """
        logger.debug("Writing configuration to device")
        self.driver.write_burst(addresses.IOCFG2, self.configurator._registers)
        self.driver.write_burst(addresses.PATABLE, self.configurator._patable)

    def load_preset(self, preset):
        """
        Load predefined configuration preset for the CC1101 module.

        This method sets the configuration registers and PA table according to a given preset
        configuration dictionary.

        Args:
            preset (dict): A dictionary containing the preset configuration with the following keys:
                - 'name': String identifier of the preset
                - 'registers': List of register configurations
                - 'patable': Power amplifier table values

        Example:
        >>> preset = {
                'name': 'my_config',
                'registers': [...],
                'patable': [...]
            }
        >>> cc1101.load_preset(preset)
        """
        logger.debug(f"Loading preset {preset['name']}")
        self.configurator._registers = preset["registers"]
        self.configurator._patable = preset["patable"]
        self.set_configuration()
    
    def idle(self):
        """Sets the CC1101 device to IDLE state.

        This state reduces power consumption by stopping all active transmission
        or reception operations. The device remains powered on and configured,
        but does not process incoming or outgoing data.

        Returns:
            None
        """
        logger.info("Setting device to IDLE state")
        self.driver.command_strobe(addresses.SIDLE)

    def set_receive_mode(self):
        """
        Sets the CC1101 device to receive mode by sending the SRX strobe command.

        The method sends the SRX (RX enable) command strobe to the CC1101 device,
        which switches it to receive mode. After sending the command, it waits for
        10ms to ensure the mode change is complete.

        Returns:
            None
        """
        logger.info("Setting device to receive mode")
        self.driver.command_strobe(addresses.SRX)
        time.sleep(0.01)

    def transmit(self, data:bytes, blocking=True):
        """Transmit the data.

        In variable length mode, the first byte of the TX FIFO must be the length byte. It 
        will be automatically set by this function.

        Args:
            data (bytes): The data to transmit.
            blocking (bool): If True, the function will block until the transmission is complete.
        """
        logger.info(f"Transmitting data {data}")
        packet_length_mode = self.configurator.get_packet_length_mode()
        expected_packet_length = self.configurator.get_packet_length()
        if packet_length_mode == 0: # fixed length mode
            if len(data) != expected_packet_length:
                logger.error(f"Data length {len(data)} does not match expected length {expected_packet_length}")
                raise ValueError(f"Data length {len(data)} does not match expected length {expected_packet_length}")
        elif packet_length_mode == 1: # variable length mode
            if len(data) > expected_packet_length:
                logger.error(f"Data length {len(data)} exceeds the maximum packet length {expected_packet_length}")
                raise ValueError(f"Data length {len(data)} exceeds the maximum packet length {expected_packet_length}")
            data = bytes([len(data)]) + data

        marc_state = self.get_marc_state()
        if marc_state != addresses.MARCSTATE_IDLE:
            logger.error(f"Device must be in state IDLE(0x01) before transmitting. Current state: 0x{marc_state:02X}")
            raise ValueError(f"Device must be in state IDLE(0x01) before transmitting. Current state: 0x{marc_state:02X}")
        
        self.driver.command_strobe(addresses.SFTX) # flush the TX FIFO
        self.driver.command_strobe(addresses.STX) # start transmitting
        for i in range(0, len(data)//self.driver.chunk_size + 1):
            while self.driver.read_status_register(addresses.TXBYTES) > 55-self.driver.chunk_size:
                time.sleep(self.driver.fifo_rw_interval)
            self.driver.write_burst(addresses.TXFIFO, list(data[self.driver.chunk_size*i: min(self.driver.chunk_size*(i+1), len(data))])) # write the data to the TX FIFO
            
        
        if blocking:
            #if self.driver.gdo0 is not None:
            #    # Start transmission
            #    self.driver.wait_for_edge(self.driver.gdo0, GPIO.RISING, 1000)

            if self.driver.gdo0 is not None:
                # End of transmission
                self.driver.wait_for_edge(self.driver.gdo0, GPIO.FALLING, 1000)
        
    def receive(self, blocking=True, timeout_ms=1000):
        """Receive data.

        Args:
            blocking (bool): If True, the function will block until data is received.

        Returns:
            bytes: The received data.
        """
        logger.info("Receiving data")
        marc_state = self.get_marc_state()
        if marc_state != addresses.MARCSTATE_IDLE:
            logger.error(f"Device must be in state IDLE(0x01) before receiving. Current state: 0x{marc_state:02X}")
            raise ValueError(f"Device must be in state IDLE(0x01) before receiving. Current state: 0x{marc_state:02X}")
        
        self.driver.command_strobe(addresses.SRX) # start receiving
        if blocking:
            if self.driver.gdo0 is not None:
                # Start reception
                if self.driver.wait_for_edge(self.driver.gdo0, GPIO.RISING, timeout=timeout_ms) is None:
                    logger.warning("Timeout waiting for start of reception")
                    return None
        data = []
        while (self.driver.read_gdo0() == GPIO.HIGH):
            trunc = self.driver.read_burst(addresses.RXFIFO, self.driver.read_status_register(addresses.RXBYTES)-1)
            if trunc is not None:
                data += trunc
            time.sleep(self.driver.fifo_rw_interval)
        trunc = self.driver.read_burst(addresses.RXFIFO, self.driver.read_status_register(addresses.RXBYTES))
        data += trunc
        #self.driver.command_strobe(addresses.SIDLE)
        
        length = None
        rssi = None
        lqi = None
        crc_ok = False

        if self.configurator.get_packet_length_mode() == 0: # fixed length mode
            length = len(data)
        elif self.configurator.get_packet_length_mode() == 1: # variable length mode
            length = data[0]
            data = data[1:]

        if self.configurator.get_append_status_enabled():
            rssi = data[-2]
            lqi = data[-1] & 0x7F
            crc_ok = data[-1] & 0x80 == 0x80
            data = data[:-2]
            length -= 2
        
        packet = Received_Packet(bytes(data), length, rssi, lqi, crc_ok)
        return packet
        

    def get_marc_state(self):
        """
        Retrieve the current MARC state from the CC1101 transceiver.

        This method reads the MARCSTATE status register from the CC1101 transceiver
        using the driver and returns its value. The MARCSTATE register provides
        information about the current state of the main radio control state machine.

        The possible states are:
            0x00: SLEEP
            0x01: IDLE
            0x02: XOFF
            0x03: VCOON_MC
            0x04: REGON_MC
            0x05: MANCAL
            0x06: VCOON
            0x07: REGON
            0x08: STARTCAL
            0x09: BWBOOST
            0x0A: FS_LOCK
            0x0B: IFADCON
            0x0C: ENDCAL
            0x0D: RX
            0x0E: RX_END
            0x0F: RX_RST
            0x10: TXRX_SWITCH
            0x11: RXFIFO_OVERFLOW
            0x12: FSTXON
            0x13: TX
            0x14: TX_END
            0x15: RXTX_SWITCH
            0x16: TXFIFO_UNDERFLOW

        Returns:
            int: The value of the MARCSTATE status register.
        """
        return self.driver.read_status_register(addresses.MARCSTATE)