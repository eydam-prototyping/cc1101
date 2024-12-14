import epCC1101.addresses as addr
import epCC1101.options as opt
from epCC1101.presets import rf_setting_dr1k2_dev5k2_2fsk_rxbw58k_sens
import math
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Cc1101Configurator:
    _preamble_lengths = [2, 3, 4, 6, 8, 12, 16, 24]
    def __init__(self, preset=rf_setting_dr1k2_dev5k2_2fsk_rxbw58k_sens, fosc=26e6):
        self._preset = preset
        self._registers = preset["registers"]
        self._patable = preset["patable"]
        self._fosc = fosc


    def get_data_rate_baud(self):
        """see 12 Data Rate Programming

        Returns:
            int: Data rate in baud
        """
        
        drate_e = self._registers[addr.MDMCFG4] & 0x0F
        drate_m = self._registers[addr.MDMCFG3] & 0xFF
        
        return round((256 + drate_m) * (self._fosc / 2**28) * 2**drate_e)
        
    def set_data_rate_baud(self, drate_baud: int):
        """see 12 Data Rate Programming
        Args:
            drate_baud (int): Data rate in baud
        """
        drate_e = math.floor(
            math.log2(drate_baud * 2**20 / self._fosc)
        )
        drate_m = round(
            drate_baud * 2**28 / (self._fosc * 2**drate_e) - 256
        )
        if drate_m == 256:
            drate_e += 1
            drate_m = 0
        self._registers[addr.MDMCFG4] = (self._registers[addr.MDMCFG4] & 0xF0) | drate_e
        self._registers[addr.MDMCFG3] = drate_m


    def get_receiver_bandwidth_hz(self):
        """see 13 Receiver Channel Filter Bandwidth

        Returns:
            int: Receiver bandwidth in Hz
        """
        rxbw_e = self._registers[addr.MDMCFG4] >> 6
        rxbw_m = self._registers[addr.MDMCFG4] >> 4 & 0x03
        return round(self._fosc / (8 * (4 + rxbw_m) * 2**rxbw_e))

    def set_receiver_bandwidth_hz(self, rxbw_hz: int):
        """see 13 Receiver Channel Filter Bandwidth

        Args:
            rxbw_hz (int): Receiver bandwidth in Hz
        """
        rxbw_e = math.floor(
            math.log2(self._fosc / (rxbw_hz * 8)) - 2
        )
        rxbw_m = round(
            (self._fosc / (rxbw_hz * 8)) / 2**rxbw_e - 4
        )
        self._registers[addr.MDMCFG4] = (self._registers[addr.MDMCFG4] & 0x0F) | (rxbw_e << 6) | (rxbw_m << 4)

    def get_frequency_offset_compensation_setting(self) -> tuple[int ,int ,int ,int]:
        """see 14.1 Frequency Offset Compensation
        
        Returns:
            tuple: 
                FOC_BS_CS_GATE: 
                    0: Frequency offset compensation always on
                    1: Frequency offset compensation freezes until carrier sense is asserted
                FOC_PRE_K: The frequency compensation loop gain to be used before a sync word is detected.
                    0: K
                    1: 2K
                    2: 3K
                    3: 4K
                FOC_POST_K: The frequency compensation loop gain to be used after a sync word is detected.
                    0: same as FOC_PRE_K
                    1: K/2
                FOC_LIMIT: The saturation point for the frequency offset compensation algorithm:
                    0: ±0 No compensation
                    1: ±BW_CHAN/8 
                    2: ±BW_CHAN/4
                    3: ±BW_CHAN/2
                    Must be set to 0 for ASK/OOK modulation
        """
        FOC_BS_CS_GATE = self._registers[addr.FOCCFG] >> 5 & 0x01
        FOC_PRE_K = self._registers[addr.FOCCFG] >> 3 & 0x03
        FOC_POST_K = self._registers[addr.FOCCFG] >> 2 & 0x01
        FOC_LIMIT = self._registers[addr.FOCCFG] & 0x03
        return  FOC_BS_CS_GATE, FOC_PRE_K, FOC_POST_K, FOC_LIMIT

    def set_frequency_offset_compensation_setting(self, FOC_BS_CS_GATE: int, FOC_PRE_K: int, FOC_POST_K: int, FOC_LIMIT: int):
        """see 14.1 Frequency Offset Compensation

        FOC_BS_CS_GATE: 
            0: Frequency offset compensation always on
            1: Frequency offset compensation freezes until carrier sense is asserted
        FOC_PRE_K: The frequency compensation loop gain to be used before a sync word is detected.
            0: K
            1: 2K
            2: 3K
            3: 4K
        FOC_POST_K: The frequency compensation loop gain to be used after a sync word is detected.
            0: same as FOC_PRE_K
            1: K/2
        FOC_LIMIT: The saturation point for the frequency offset compensation algorithm:
            0: ±0 No compensation
            1: ±BW_CHAN/8 
            2: ±BW_CHAN/4
            3: ±BW_CHAN/2
            Must be set to 0 for ASK/OOK modulation

        Args:
            FOC_BS_CS_GATE (int): see get_frequency_offset_compensation_setting
            FOC_PRE_K (int): see get_frequency_offset_compensation_setting
            FOC_POST_K (int): see get_frequency_offset_compensation_setting
            FOC_LIMIT (int): see get_frequency_offset_compensation_setting
        """
        self._registers[addr.FOCCFG] =\
              (FOC_BS_CS_GATE << 5) | \
              (FOC_PRE_K << 3) | \
              (FOC_POST_K << 2) | FOC_LIMIT

    def get_sync_mode(self) -> int:
        """see 14.3 Byte Synchronization

        Returns:
            int: Sync mode:
                0: No preamble/sync
                1: 15/16 sync word bits detected
                2: 16/16 sync word bits detected
                3: 30/32 sync word bits detected
                4: No preamble/sync, carrier-sense above threshold
                5: 15/16 + carrier-sense above threshold
                6: 16/16 + carrier-sense above threshold
                7: 30/32 + carrier-sense above threshold
        """
        return self._registers[addr.MDMCFG2] & 0x07
    
    def set_sync_mode(self, sync_mode: int):
        """see 14.3 Byte Synchronization\
        

        Options:

            0: No preamble/sync
            1: 15/16 sync word bits detected
            2: 16/16 sync word bits detected
            3: 30/32 sync word bits detected
            4: No preamble/sync, carrier-sense above threshold
            5: 15/16 + carrier-sense above threshold
            6: 16/16 + carrier-sense above threshold
            7: 30/32 + carrier-sense above threshold
        
        Args:
            sync_mode (int): see get_sync_mode
        """
        self._registers[addr.MDMCFG2] = (self._registers[addr.MDMCFG2] & 0xF8) | sync_mode

    def get_sync_word(self):
        """see 14.3 Byte Synchronization

        Returns:
            [int, int]: Sync word
        """
        return self._registers[addr.SYNC1:addr.SYNC0+1]
    
    def set_sync_word(self, sync_word):
        """see 14.3 Byte Synchronization

        Args:
            sync_word ([int, int]): Sync word
        """
        self._registers[addr.SYNC1:addr.SYNC0+1] = sync_word

    def get_data_whitening_enable(self) -> bool:
        """see 15.1 Data Whitening

        Returns:
            bool: Data whitening enabled
        """
        return (self._registers[addr.PKTCTRL0] >> 6) & 0x01

    def set_data_whitening_enable(self, enable: bool):
        """see 15.1 Data Whitening

        """
        self._registers[addr.PKTCTRL0] = (self._registers[addr.PKTCTRL0] & 0xBF) | (enable << 6)

    def get_preamble_length_bytes(self) -> int:
        """see 15.2 Packet Format

        Returns:
            int: Preamble length in bytes
        """
        return self._preamble_lengths[self._registers[addr.MDMCFG1] >> 4 & 0x07]

    def set_preamble_length_bytes(self, preamble_length: int):
        """see 15.2 Packet Format

        Valid values are 2, 3, 4, 6, 8, 12, 16, 24

        raise ValueError if preamble_length is invalid
        """
        if preamble_length not in self._preamble_lengths:
            raise ValueError(f"Invalid preamble length: {preamble_length}. Must be one of {self._preamble_lengths}")
        
        self._registers[addr.MDMCFG1] = (self._registers[addr.MDMCFG1] & 0x8F) | (self._preamble_lengths.index(preamble_length) << 4)

    def get_packet_length_mode(self) -> int:
        """see 15.2 Packet Format

        Returns:
            int: Packet length mode
                0: Fixed packet length mode
                1: Variable packet length mode
                2: Infinite packet length mode
        """
        return self._registers[addr.PKTCTRL0] & 0x03
    
    def set_packet_length_mode(self, mode: int):
        """see 15.2 Packet Format\
        
        Options:
        
            0: Fixed packet length mode
            1: Variable packet length mode
            2: Infinite packet length mode

        Args:
            mode (int): see get_packet_length_mode
        """
        self._registers[addr.PKTCTRL0] = (self._registers[addr.PKTCTRL0] & 0xFC) | mode

    def get_packet_length(self):
        """see 15.2 Packet Format

        Returns:
            int: Packet length
        """
        return self._registers[addr.PKTLEN]
    
    def set_packet_length(self, length: int):
        """see 15.2 Packet Format

        Args:
            length (int): Packet length
        """
        self._registers[addr.PKTLEN] = length

    def get_crc_enable(self) -> bool:
        """see 15.2 Packet Format

        Returns:
            bool: CRC enabled
        """
        return (self._registers[addr.PKTCTRL0] >> 2) & 0x01

    def set_crc_enable(self, enable: bool):
        """see 15.2 Packet Format

        Args:
            enable (bool): CRC enabled
        """
        self._registers[addr.PKTCTRL0] = (self._registers[addr.PKTCTRL0] & 0xFB) | (enable << 2)

    def get_address_check_mode(self) -> int:
        """see 15.2 Packet Format

        Returns:
            int: Address check mode
                0: No address check
                1: Address check, no broadcast
                2: Address check, 0 (0x00) broadcast
                3: Address check, 0 (0x00) and 255 (0xFF) broadcast
        """
        return self._registers[addr.PKTCTRL1] & 0x03

    def set_address_check_mode(self, mode: int):
        """see 15.2 Packet Format\

        Options:

            0: No address check
            1: Address check, no broadcast
            2: Address check, 0 (0x00) broadcast
            3: Address check, 0 (0x00) and 255 (0xFF) broadcast

        Args:
            mode (int): see get_address_check_mode
        """
        self._registers[addr.PKTCTRL1] = (self._registers[addr.PKTCTRL1] & 0xFC) | mode

    def get_address(self):
        """see 15.2 Packet Format

        Returns:
            int: Address
        """
        return self._registers[addr.ADDR]
    
    def set_address(self, address: int):
        """see 15.2 Packet Format

        Args:
            address (int): Address
        """
        self._registers[addr.ADDR] = address

    def get_crc_auto_flush(self) -> bool:
        """see 15.3 Packet Filtering in RX

        Returns:
            bool: CRC auto flush enabled
        """
        return self._registers[addr.PKTCTRL1] >> 3 & 0x01

    def set_crc_auto_flush(self, enable: bool):
        """see 15.3 Packet Filtering in RX

        Args:
            enable (bool): CRC auto flush enabled
        """
        self._registers[addr.PKTCTRL1] = (self._registers[addr.PKTCTRL1] & 0xF7) | (enable << 3)

    def get_append_status_enabled(self) -> bool:
        """see 15.3 Packet Filtering in RX

        Returns:
            bool: Append status enabled
        """
        return self._registers[addr.PKTCTRL1] >> 2 & 0x01
    
    def set_append_status_enabled(self, enable: bool):
        """see 15.3 Packet Filtering in RX

        Args:
            enable (bool): Append status enabled
        """
        self._registers[addr.PKTCTRL1] = (self._registers[addr.PKTCTRL1] & 0xFB) | (enable << 2)

    def get_fec_enable(self) -> bool:
        """see 15.4 Packet Handling in Transmit Mode
        and 18.1 Forward Error Correction (FEC)

        Returns:
            bool: Forward Error Correction (FEC) enabled
        """
        return self._registers[addr.MDMCFG2] >> 7 & 0x01

    def set_fec_enable(self, enable: bool):
        """see 15.4 Packet Handling in Transmit Mode
        and 18.1 Forward Error Correction (FEC)

        Args:
            enable (bool): Forward Error Correction (FEC) enabled
        """
        self._registers[addr.MDMCFG2] = (self._registers[addr.MDMCFG2] & 0x7F) | (enable << 7)

    def get_GDOx_config(self, GDOx: int) -> int:
        """see 15.5 Packet Handling in Firmware
        and 26 General Purpose / Test Output Control Pins

        Args:
            GDOx (int): GDOx pin number

        Returns:
            int: GDOx configuration
        """
        return self._registers[addr.IOCFG2 + (2-GDOx)] & 0x3F
    
    def set_GDOx_config(self, GDOx: int, config: int):
        """see 15.5 Packet Handling in Firmware
        and 26 General Purpose / Test Output Control Pins

        Args:
            GDOx (int): GDOx pin number
            config (int): GDOx configuration
        """
        self._registers[addr.IOCFG2 + (2-GDOx)] = config

    def get_GDOx_inverted(self, GDOx: int) -> bool:
        """see 26 General Purpose / Test Output Control Pins

        Args:
            GDOx (int): GDOx pin number

        Returns:
            bool: GDOx inverted
        """
        return self._registers[addr.IOCFG2 + (2-GDOx)] >> 6 & 0x01
    
    def set_GDOx_inverted(self, GDOx: int, inverted: bool):
        """see 26 General Purpose / Test Output Control Pins

        Args:
            GDOx (int): GDOx pin number
            inverted (bool): GDOx inverted
        """
        self._registers[addr.IOCFG2 + (2-GDOx)] = (self._registers[addr.IOCFG2 + (2-GDOx)] & 0xBF) | (inverted << 6)

    def get_modulation_format(self) -> int:
        """see 16 Modulation Format

        Returns:
            int: Modulation format
                0: 2-FSK
                1: GFSK
                3: ASK/OOK
                4: 4-FSK
                7: MSK
        """
        return self._registers[addr.MDMCFG2] >> 4 & 0x07
    
    def set_modulation_format(self, format: int):
        """see 16 Modulation Format\

        Options:
            
            0: 2-FSK
            1: GFSK
            3: ASK/OOK
            4: 4-FSK
            7: MSK
        
        Args:
            format (int): Modulation format
        """
        self._registers[addr.MDMCFG2] = (self._registers[addr.MDMCFG2] & 0x8F) | (format << 4)
        # set FREND0 register to 1 for ASK/OOK modulation
        if format == 3:
           self._registers[addr.FREND0] = (self._registers[addr.FREND0] & 0xF7) | 0x01
        else:
            self._registers[addr.FREND0] = (self._registers[addr.FREND0] & 0xF7)
    
    def get_manchester_encoding_enable(self) -> bool:
        """see 16 Modulation Format

        Returns:
            bool: Manchester encoding enabled
        """
        return (self._registers[addr.MDMCFG2] >> 3) & 0x01

    def set_manchester_encoding_enable(self, enable: bool):
        """see 16 Modulation Format

        Args:
            enable (bool): Manchester encoding enabled
        """
        self._registers[addr.MDMCFG2] = (self._registers[addr.MDMCFG2] & 0xF7) | (enable << 3)

    def get_deviation_hz(self):
        """see 16.1 Frequency Shift Keying
        only valid for 2-FSK, 4-FSK and GFSK

        Returns:
            int: Frequency deviation in Hz
        """
        dev_e = self._registers[addr.DEVIATN] >> 4 & 0x07
        dev_m = self._registers[addr.DEVIATN] & 0x07
        return (8 + dev_m) * (self._fosc / 2**17) * 2**dev_e
    
    def set_deviation_hz(self, deviation_hz: int):
        """see 16.1 Frequency Shift Keying

        Args:
            deviation_hz (int): Frequency deviation in Hz
        """
        dev_e = math.floor(
            math.log2(deviation_hz * 2**15 / self._fosc)
        ) - 1
        dev_m = math.floor(
            deviation_hz * 2**17 / (self._fosc * 2**dev_e) - 8
        )
        self._registers[addr.DEVIATN] = (dev_e << 4) | dev_m 

    def get_base_frequency_hz(self):
        """see 21 Frequency Programming
        
        Returns:
            int: Base frequency in Hz
        """
        return round(int.from_bytes(self._registers[addr.FREQ2:addr.FREQ0+1], 'big')*self._fosc/2**16)

    def set_base_frequency_hz(self, freq_hz):
        """see 21 Frequency Programming

        Args:
            freq_hz (int): Base frequency in Hz
        """
        freq = round(freq_hz*2**16/self._fosc).to_bytes(3, 'big')
        self._registers[addr.FREQ2:addr.FREQ0+1] = [freq[0], freq[1], freq[2]]

    def get_patable(self):
        """see 10.6 PATABLE Access

        Returns:
            [int]: PATABLE values
        """
        return self._patable
    
    def set_patable(self, patable):
        """see 10.6 PATABLE Access

        Args:
            patable ([int]): PATABLE values
        """
        self._patable = patable
    

    def print_description(self):
        logger.info(f"12   Data rate: {self.get_data_rate_baud()/1e3:.3f} kbps")

        logger.info(f"13   Receiver bandwidth: {self.get_receiver_bandwidth_hz()/1e3:.3f} kHz")
 
        frequency_offset_compensation_setting = self.get_frequency_offset_compensation_setting()
        logger.info(f"14.1 Frequency offset compensation setting:")
        logger.info(f"     FOC_BS_CS_GATE: {frequency_offset_compensation_setting[0]} ({opt.FOC_BS_CS_GATE_OPTIONS[frequency_offset_compensation_setting[0]]})")
        logger.info(f"     FOC_PRE_K: {frequency_offset_compensation_setting[1]} ({opt.FOC_PRE_K_OPTIONS[frequency_offset_compensation_setting[1]]})")
        logger.info(f"     FOC_POST_K: {frequency_offset_compensation_setting[2]} ({opt.FOC_POST_K_OPTIONS[frequency_offset_compensation_setting[2]]})")
        logger.info(f"     FOC_LIMIT: {frequency_offset_compensation_setting[3]} ({opt.FOC_LIMIT[frequency_offset_compensation_setting[3]]})")
        logger.info(f"14.3 Byte synchronization mode: {self.get_sync_mode()} ({opt.BYTE_SYNCHRONIZATION_MODES[self.get_sync_mode()]})")
        logger.info(f"14.3 Synchronization word: 0x{self.get_sync_word()[0]:02X}{self.get_sync_word()[1]:02X}")
        
        logger.info(f"15.1 Data whitening: {self.get_data_whitening_enable()}")  
        logger.info(f"15.2 Preamble length: {self.get_preamble_length_bytes()} bytes")
        logger.info(f"     Packet length mode: {self.get_packet_length_mode()} ({opt.PAKET_LENGTH_OPTIONS[self.get_packet_length_mode()]})")
        logger.info(f"     Packet length: {self.get_packet_length()} bytes")
        logger.info(f"     CRC enabled: {self.get_crc_enable()}")
        logger.info(f"     Address check mode: {self.get_address_check_mode()} ({opt.ADDRESS_CHECK_OPTIONS[self.get_address_check_mode()]})")
        logger.info(f"     Address: {self.get_address()}")
        logger.info(f"15.3 CRC auto flush: {self.get_crc_auto_flush()}")
        logger.info(f"     Append status: {self.get_append_status_enabled()}")
        logger.info(f"15.4 FEC enabled: {self.get_fec_enable()}")
        logger.info(f"15.5 GDO0 configuration: 0x{self.get_GDOx_config(0):02X}")
        logger.info(f"     GDO1 configuration: 0x{self.get_GDOx_config(1):02X}")
        logger.info(f"     GDO2 configuration: 0x{self.get_GDOx_config(2):02X}")
        logger.info(f"     GDO0 inverted: {self.get_GDOx_inverted(0)}")
        logger.info(f"     GDO1 inverted: {self.get_GDOx_inverted(1)}")
        logger.info(f"     GDO2 inverted: {self.get_GDOx_inverted(2)}")

        logger.info(f"16   Modulation format: {self.get_modulation_format()} ({opt.MODULATION_FORMAT_OPTIONS[self.get_modulation_format()]})")
        logger.info(f"     Manchester encoding: {self.get_manchester_encoding_enable()}")
        logger.info(f"16.1 Frequency deviation: {self.get_deviation_hz()/1e3:.3f} kHz")

        logger.info(f"21   Base frequency: {self.get_base_frequency_hz()/1e6:.3f} MHz")