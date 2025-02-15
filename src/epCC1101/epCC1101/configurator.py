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
        
        return int(round((256 + drate_m) * (self._fosc / 2**28) * 2**drate_e))
        
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
        assert 0 <= sync_mode <= 7, f"Invalid sync mode: {sync_mode}. Must be between 0 and 7"
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
            math.log2(deviation_hz * 2**14 / self._fosc)
        )
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

    def get_channel_spacing_hz(self):
        """see 21 Frequency Programming

        Returns:
            int: Channel spacing in Hz
        """
        spacing_e = self._registers[addr.MDMCFG1] & 0x03
        spacing_m = self._registers[addr.MDMCFG0]
        return round((256 + spacing_m) * (self._fosc / 2**18) * 2**spacing_e)
        
    def set_channel_spacing_hz(self, spacing_hz: int):
        """see 21 Frequency Programming

        Args:
            spacing_hz (int): Channel spacing in Hz
        """
        spacing_e = math.floor(
            math.log2(spacing_hz * 2**10 / self._fosc)
        )
        spacing_m = round(
            spacing_hz * 2**18 / (self._fosc * 2**spacing_e) - 256
        )
        if spacing_m == 256:
            spacing_e += 1
            spacing_m = 0

        self._registers[addr.MDMCFG1] = (self._registers[addr.MDMCFG1] & 0xFC) | spacing_e
        self._registers[addr.MDMCFG0] = spacing_m

    def get_channel_number(self):
        """see 21 Frequency Programming

        Returns:
            int: Channel number
        """
        return self._registers[addr.CHANNR]
    
    def set_channel_number(self, channel: int):
        """see 21 Frequency Programming

        Args:
            channel (int): Channel number
        """
        assert 0 <= channel <= 255, f"Invalid channel number: {channel}. Must be between 0 and 255"
        self._registers[addr.CHANNR] = channel

    def get_packet_format(self):
        """see 27 Asynchronous and Synchronous Serial Operation

        Returns:
            [int]: Packet format
        """
        return (self._registers[addr.PKTCTRL0] >> 4) & 0x03

    def set_packet_format(self, packet_format):
        """see 27 Asynchronous and Synchronous Serial Operation

        Args:
            packet_format ([int]): Packet format
        """
        assert 0 <= packet_format <= 3, f"Invalid packet format: {packet_format}. Must be between 0 and 3"
        
        if packet_format == 0: # Packet mode
            self.set_GDOx_config(0, 0x06) # Sync word detect
            # GDO2 don't care
        elif packet_format == 1: # Sync serial mode
            self.set_GDOx_config(0, 0x0C) # Serial Synchronous Data Output
            self.set_GDOx_config(2, 0x0B) # Serial Clock
        elif packet_format == 3: # Asynchronous serial mode
            self.set_GDOx_config(0, 0x0E) # Carrier sense
            self.set_GDOx_config(2, 0x0D) # Serial Asynchronous Data Output

        self._registers[addr.PKTCTRL0] = (self._registers[addr.PKTCTRL0] & 0xCF) | (packet_format << 4)

    def get_agc_filter_length(self):
        """see ???
        
        2-FSK, 4-FSK, MSK: Sets the averaging length for the amplitude from the channel filter.  
        
        ASK, OOK: Sets the OOK/ASK decision boundary for OOK/ASK reception. 
        
        Value: Channel filter samples / OOK/ASK decision boundary
        0: 8 samples / 4 dB
        1: 16 samples / 8 dB
        2: 32 samples / 12 dB
        3: 64 samples / 16 dB
        
        Returns:
            int: AGC filter length
        """
        return self._registers[addr.AGCCTRL0] & 0x03
    
    def set_agc_filter_length(self, length):
        """see ???

        Args:
            length ([type]): AGC filter length
        """
        assert 0 <= length <= 3, f"Invalid AGC filter length: {length}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL0] = (self._registers[addr.AGCCTRL0] & 0xFC) | length

    def get_agc_freeze(self):
        """see ???

        Returns:
            int: AGC freeze
        """
        return (self._registers[addr.AGCCTRL0] >> 2) & 0x03

    def set_agc_freeze(self, freeze):
        """see ???

        Args:
            freeze ([type]): AGC freeze
        """
        assert 0 <= freeze <= 3, f"Invalid AGC freeze: {freeze}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL0] = (self._registers[addr.AGCCTRL0] & 0xF3) | (freeze << 2)

    def get_agc_wait_time(self):
        """see ???

        Returns:
            int: AGC wait time
        """
        return (self._registers[addr.AGCCTRL0] >> 4) & 0x03
    
    def set_agc_wait_time(self, wait_time):
        """see ???

        Args:
            wait_time ([type]): AGC wait time
        """
        assert 0 <= wait_time <= 3, f"Invalid AGC wait time: {wait_time}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL0] = (self._registers[addr.AGCCTRL0] & 0xCF) | (wait_time << 4)

    def get_agc_hyst_level(self):
        """see ???

        Returns:
            int: AGC hysteresis level
        """
        return (self._registers[addr.AGCCTRL0] >> 6) & 0x03

    def set_agc_hyst_level(self, hyst_level):
        """see ???

        Args:
            hyst_level ([type]): AGC hysteresis level
        """
        assert 0 <= hyst_level <= 3, f"Invalid AGC hysteresis level: {hyst_level}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL0] = (self._registers[addr.AGCCTRL0] & 0x3F) | (hyst_level << 6)

    def get_agc_carrier_sense_absolute_threshold(self):
        """see ???

        Returns:
            int: AGC carrier sense absolute threshold
        """
        return self._registers[addr.AGCCTRL1] & 0x0F
    
    def set_agc_carrier_sense_absolute_threshold(self, threshold):
        """see ???

        Args:
            threshold ([type]): AGC carrier sense absolute threshold
        """
        assert 0 <= threshold <= 15, f"Invalid AGC carrier sense absolute threshold: {threshold}. Must be between 0 and 15"
        self._registers[addr.AGCCTRL1] = (self._registers[addr.AGCCTRL1] & 0xF0) | threshold
    
    def get_agc_carrier_sense_relative_threshold(self):
        """see ???

        Returns:
            int: AGC carrier sense relative threshold
        """
        return (self._registers[addr.AGCCTRL1] >> 4) & 0x03
    
    def set_agc_carrier_sense_relative_threshold(self, threshold):
        """see ???

        Args:
            threshold ([type]): AGC carrier sense relative threshold
        """
        assert 0 <= threshold <= 3, f"Invalid AGC carrier sense relative threshold: {threshold}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL1] = (self._registers[addr.AGCCTRL1] & 0xCF) | (threshold << 4)

    def get_agc_lna_priority(self):
        """see ???

        Returns:
            bool: AGC LNA priority
        """
        return (self._registers[addr.AGCCTRL1] >> 6) & 0x01
    
    def set_agc_lna_priority(self, priority):
        """see ???

        Args:
            priority ([type]): AGC LNA priority
        """
        assert 0 <= priority <= 1, f"Invalid AGC LNA priority: {priority}. Must be 0 or 1"
        self._registers[addr.AGCCTRL1] = (self._registers[addr.AGCCTRL1] & 0xBF) | (priority << 6)

    def get_agc_magn_target(self):
        """see ???

        Returns:
            int: MAGN_TARGET
        """
        return self._registers[addr.AGCCTRL2] & 0x07
    
    def set_agc_magn_target(self, target):
        """see ???

        Args:
            target ([type]): MAGN_TARGET
        """
        assert 0 <= target <= 7, f"Invalid MAGN_TARGET: {target}. Must be between 0 and 7"
        self._registers[addr.AGCCTRL2] = (self._registers[addr.AGCCTRL2] & 0xF8) | target

    def get_agc_max_lna_gain(self):
        """see ???

        Returns:
            int: MAX_LNA_GAIN
        """
        return (self._registers[addr.AGCCTRL2] >> 3) & 0x07
    
    def set_agc_max_lna_gain(self, gain):
        """see ???

        Args:
            gain ([type]): MAX_LNA_GAIN
        """
        assert 0 <= gain <= 7, f"Invalid MAX_LNA_GAIN: {gain}. Must be between 0 and 7"
        self._registers[addr.AGCCTRL2] = (self._registers[addr.AGCCTRL2] & 0xC7) | (gain << 3)

    def get_agc_max_dvga_gain(self):
        """see ???

        Returns:
            int: MAX_DVGA_GAIN
        """
        return (self._registers[addr.AGCCTRL2] >> 6) & 0x03
    
    def set_agc_max_dvga_gain(self, gain):
        """see ???

        Args:
            gain ([type]): MAX_DVGA_GAIN
        """
        assert 0 <= gain <= 3, f"Invalid MAX_DVGA_GAIN: {gain}. Must be between 0 and 3"
        self._registers[addr.AGCCTRL2] = (self._registers[addr.AGCCTRL2] & 0x3F) | (gain << 6)


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
        assert 1 <= len(patable) <= 8, f"Invalid PATABLE length: {len(patable)}. Must be between 1 and 8"
        assert all(0 <= value <= 0xFF for value in patable), f"Invalid PATABLE values: {patable}. Must be between 0 and 0xFF"
        self._patable = patable
    
    def print_registers(self):
        for i, value in enumerate(self._registers):
            logger.info(f"{i:02X}: {value:02X}")

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

        logger.info(f"27   Packet format: {self.get_packet_format()}")

        logger.info(f"XXX  AGC filter length: {self.get_agc_filter_length()}")
        logger.info(f"     AGC freeze: {self.get_agc_freeze()}")
        logger.info(f"     AGC wait time: {self.get_agc_wait_time()}")
        logger.info(f"     AGC hysteresis level: {self.get_agc_hyst_level()}")
        logger.info(f"     AGC carrier sense absolute threshold: {self.get_agc_carrier_sense_absolute_threshold()}")
        logger.info(f"     AGC carrier sense relative threshold: {self.get_agc_carrier_sense_relative_threshold()}")
        logger.info(f"     AGC LNA priority: {self.get_agc_lna_priority()}")
        logger.info(f"     AGC magnitude target: {self.get_agc_magn_target()}")
        logger.info(f"     AGC max LNA gain: {self.get_agc_max_lna_gain()}")
        logger.info(f"     AGC max DVGA gain: {self.get_agc_max_dvga_gain()}")