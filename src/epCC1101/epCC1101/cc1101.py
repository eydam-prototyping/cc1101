import sys
import epCC1101.addresses as addresses
from epCC1101.configurator import Cc1101Configurator
from epCC1101.driver import Abstract_Driver
import logging

if sys.implementation.name == "micropython":
    raise NotImplementedError("This library is not compatible with MicroPython")
elif sys.implementation.name == "cpython":
    if sys.platform == "linux":
        import RPi.GPIO as GPIO
        import pigpio
    if sys.platform.startswith("win"):
        from epCC1101.stubs import GPIO
        from epCC1101.stubs import pigpio

import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Received_Packet:
    def __init__(self, timestamp:float, length_s:float, configurator:Cc1101Configurator):
        self.timestamp = timestamp
        self.length_s = length_s
        self.configurator = configurator

class Raw_Received_Packet(Received_Packet):
    def __init__(self, edges:list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edges = edges

    def get_bitstream(self):
        bitstream = []
        t_bit = 1/self.configurator.get_data_rate_baud()
        for i in range(1, len(self.edges)):
            pulse_length = self.edges[i][1] - self.edges[i-1][1]
            bit = self.edges[i][0]
            bitstream += [1-bit] * round(pulse_length / t_bit)
        return bitstream

    def __str__(self):
        return f"Raw_Received_Packet(edges={len(self.edges)})"

class Processed_Received_Packet(Received_Packet):
    def __init__(self, payload:bytes, length:int, rssi:int, lqi:int=None, crc_ok:bool=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.payload = payload
        self.length = length
        self.rssi = rssi
        self.lqi = lqi
        self.crc_ok = crc_ok

    def __str__(self): 
        return f"Processed_Received_Packet(payload={self.payload}, length={self.length}, rssi={self.rssi}, lqi={self.lqi}, crc_ok={self.crc_ok})"

class Cc1101:
    _samples = []
    _sampling_active = False
    _packet_start = 0
    _packet_end = 0

    def __init__(self, driver:Abstract_Driver):
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
    
    def set_idle_mode(self):
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

    def set_transmit_mode(self):
        """
        Sets the CC1101 device to transmit mode by sending the STX strobe command.

        The method sends the STX (TX enable) command strobe to the CC1101 device,
        which switches it to transmit mode. After sending the command, it waits for
        10ms to ensure the mode change is complete.

        Returns:
            None
        """
        logger.info("Setting device to transmit mode")
        self.driver.command_strobe(addresses.STX)
        time.sleep(0.01)

    def flush_rx_fifo(self):
        """
        Flushes the RX FIFO of the CC1101 device.

        This method sends the SFRX command strobe to the CC1101 device, which clears
        the receive FIFO buffer. It is used to discard any remaining data in the buffer
        before starting a new reception.

        Returns:
            None
        """
        logger.info("Flushing RX FIFO")
        self.driver.command_strobe(addresses.SFRX)

    def flush_tx_fifo(self):
        """
        Flushes the TX FIFO of the CC1101 device.

        This method sends the SFTX command strobe to the CC1101 device, which clears
        the transmit FIFO buffer. It is used to discard any remaining data in the buffer
        before starting a new transmission.

        Returns:
            None
        """
        logger.info("Flushing TX FIFO")
        self.driver.command_strobe(addresses.SFTX)

    def _write_data_to_tx_fifo(self, data:bytes):
        for i in range(0, len(data)//self.driver.chunk_size + 1):
            while self._get_tx_bytes() > 55-self.driver.chunk_size:
                time.sleep(self.driver.fifo_rw_interval)
            self.driver.write_burst(addresses.TXFIFO, list(data[self.driver.chunk_size*i: min(self.driver.chunk_size*(i+1), len(data))])) # write the data to the TX FIFO
    
    def _get_rx_bytes(self):
        return self.driver.read_status_register(addresses.RXBYTES)&0x7F
    
    def _get_tx_bytes(self):
        return self.driver.read_status_register(addresses.TXBYTES)&0x7F

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
        packet_format = self.configurator.get_packet_format()

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
        
        self.flush_tx_fifo()
        self.set_transmit_mode()
        
        if packet_format == 0:  # normal mode, use the TX FIFO
            self._write_data_to_tx_fifo(data)
            if blocking:
                if self.driver.gdo0 is not None:
                    # End of transmission
                    self.driver.set_pin_mode(self.driver.gdo0, GPIO.IN)
                    self.driver.wait_for_edge(self.driver.gdo0, GPIO.FALLING, 1000)
                    self.driver.reset_pin_mode(self.driver.gdo0)
        elif packet_format == 1:  # synchronous serial mode
            self.driver.synchronous_serial_write(self.driver.gdo2, self.driver.gdo0, [int(i) for i in data], self.configurator.get_data_rate_baud())
        elif packet_format == 2:  # random mode
            pass
        elif packet_format == 3:  # asynchronous serial mode
            assert self.driver.gdo0 is not None, "GDO0 must be connected to an interrupt pin for asynchronous serial mode"
            self.driver.asynchronous_serial_write(self.driver.gdo0, self.configurator.get_data_rate_baud(), [int(i) for i in data])
        
        self.set_idle_mode()

    def receive(self, timeout_ms=1000):
        """Receive data.
        
        Returns:
            bytes: The received data.
        """
        logger.info("Receiving data")
        marc_state = self.get_marc_state()
        self._samples = []
        self._sampling_active = False
        self._packet_start = 0
        self._packet_end = 0

        if marc_state not in [addresses.MARCSTATE_IDLE, addresses.MARCSTATE_RX]:
            logger.error(f"Device must be in state IDLE(0x01) before receiving. Current state: 0x{marc_state:02X}")
            raise ValueError(f"Device must be in state IDLE(0x01) before receiving. Current state: 0x{marc_state:02X}")
        
        self.flush_rx_fifo()

        if marc_state != addresses.MARCSTATE_RX:
           self.driver.command_strobe(addresses.SRX)
    
        packet_format = self.configurator.get_packet_format()

        if packet_format == 0: # normal mode, use the RX FIFO
            assert self.configurator.get_GDOx_config(0) == 0x06, "GDO0 must be configured for sync word detection (0x06) in fixed/variable length mode"
            assert self.driver.gdo0 is not None, "GDO0 must be connected to an interrupt pin for fixed/variable length mode"
            # Start reception
            self.driver.set_pin_mode(self.driver.gdo0, GPIO.IN)
            if self.driver.wait_for_edge(self.driver.gdo0, GPIO.RISING, timeout=timeout_ms) is None:
                logger.warning("Timeout waiting for start of reception")
                return None
            self._packet_start = time.time()
            data = []
            while (self.driver.wait_for_edge(self.driver.gdo0, GPIO.FALLING, timeout=self.driver.fifo_rw_interval) is None) and (self.driver.read_gdo0() == GPIO.HIGH):
                self._packet_end = time.time()
                trunc = self.driver.read_burst(addresses.RXFIFO, self._get_rx_bytes()-1)
                if trunc is not None:
                    data += trunc
            trunc = self.driver.read_burst(addresses.RXFIFO, self._get_rx_bytes())
            data += trunc
            self.driver.reset_pin_mode(self.driver.gdo0)

            length = None
            rssi = None
            lqi = None
            crc_ok = False
            
            if self.configurator.get_packet_length_mode() == 0: # fixed length mode
                length = len(data)
            else: # variable length mode
                length = data[0]
                data = data[1:]

            if self.configurator.get_append_status_enabled() and (self.configurator.get_packet_length_mode() in [0, 1]):
                rssi = data[-2]
                lqi = data[-1] & 0x7F
                crc_ok = data[-1] & 0x80 == 0x80
                data = data[:-2]
                length -= 2

            packet = Processed_Received_Packet(
                payload=bytes(data), 
                length=length, 
                rssi=rssi, 
                lqi=lqi, 
                crc_ok=crc_ok, 
                timestamp=self._packet_start, 
                length_s=self._packet_end-self._packet_start,
                configurator=self.configurator)
            
        elif packet_format == 1: # synchronous serial mode
            time.sleep(0.1)
            packet = self.driver.synchronous_serial_read(
                self.driver.gdo0,
                self.driver.gdo2,
                timeout_ms=timeout_ms
            )
        elif packet_format == 2: # random mode
            packet = None
        elif packet_format == 3: # asynchronous serial mode
            assert self.configurator.get_GDOx_config(0) == 0x0E, "GDO0 must be configured for carrier sense (0x0E) in infinite length mode"
            assert self.configurator.get_GDOx_config(2) == 0x0D, "GDO2 must be configured for serial data output (0x0D) in infinite length mode"
            assert self.driver.gdo0 is not None, "GDO0 must be connected to an interrupt pin for infinite length mode"
            assert self.driver.gdo2 is not None, "GDO2 must be connected to an interrupt pin for infinite length mode"
            
            raw = self.driver.asynchronous_serial_read(
                self.driver.gdo0,
                self.driver.gdo2,
                timeout_ms=timeout_ms,
            )

            packet = Raw_Received_Packet(
                edges=[(x[1], x[0] - raw.start_capture) for x in raw.transitions],
                timestamp=raw.start_capture, 
                length_s=raw.end_capture - raw.start_capture,
                configurator=self.configurator)
    
        self.set_idle_mode()
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