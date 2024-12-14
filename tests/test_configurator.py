import unittest
from epCC1101 import presets
from epCC1101.configurator import Cc1101Configurator
import epCC1101.addresses as addr

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestCc1101Configurator(unittest.TestCase):
    def test_base_frequency_hz(self):
        configurator = Cc1101Configurator()

        configurator.set_base_frequency_hz(915e6)
        self.assertEqual(configurator._registers[addr.FREQ2], 0x23)
        self.assertEqual(configurator._registers[addr.FREQ1], 0x31)
        self.assertEqual(configurator._registers[addr.FREQ0], 0x3B)
        self.assertEqual(int(configurator.get_base_frequency_hz()), 914999969)

    def test_data_rate_baud(self):
        configurator = Cc1101Configurator()
        
        configurator.set_data_rate_baud(1200)
        self.assertEqual(configurator._registers[addr.MDMCFG4] & 0x0F, 0x05) # drate_e
        self.assertEqual(configurator._registers[addr.MDMCFG3] & 0xFF, 0x83) # drate_m
        self.assertEqual(int(configurator.get_data_rate_baud()), 1199)   

        configurator.set_data_rate_baud(115200)
        self.assertEqual(configurator._registers[addr.MDMCFG4] & 0x0F, 0x0C)
        self.assertEqual(configurator._registers[addr.MDMCFG3] & 0xFF, 0x22)
        self.assertEqual(int(configurator.get_data_rate_baud()), 115051)   

    def test_receiver_bandwidth_hz(self):
        configurator = Cc1101Configurator()
        
        configurator.set_receiver_bandwidth_hz(58e3)
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 6, 0x03) # rxbw_e
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 4 & 0x03, 0x03) # rxbw_m
        self.assertEqual(int(configurator.get_receiver_bandwidth_hz()), 58036)   

        configurator.set_receiver_bandwidth_hz(320e3)
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 6, 0x01)
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 4 & 0x03, 0x01)
        self.assertEqual(int(configurator.get_receiver_bandwidth_hz()), 325e3)   
        
        configurator.set_receiver_bandwidth_hz(800e3)
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 6, 0x00)
        self.assertEqual(configurator._registers[addr.MDMCFG4] >> 4 & 0x03, 0x00)
        self.assertEqual(int(configurator.get_receiver_bandwidth_hz()), 812.5e3)   

    def test_frequency_offset_compensation_setting(self):
        configurator = Cc1101Configurator()

        configurator.set_frequency_offset_compensation_setting(1, 1, 1, 1)
        self.assertEqual(configurator._registers[addr.FOCCFG], 0x2D)
        self.assertEqual(configurator.get_frequency_offset_compensation_setting(), (1, 1, 1, 1))

        configurator.set_frequency_offset_compensation_setting(0, 2, 0, 3)
        self.assertEqual(configurator._registers[addr.FOCCFG], 0x13)
        self.assertEqual(configurator.get_frequency_offset_compensation_setting(), (0, 2, 0, 3))


    def test_sync_mode(self):
        configurator = Cc1101Configurator()
        
        configurator.set_sync_mode(0x00)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x07, 0x00)
        self.assertEqual(configurator.get_sync_mode(), 0x00)
        
        configurator.set_sync_mode(0x07)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x07, 0x07)
        self.assertEqual(configurator.get_sync_mode(), 0x07)


    def test_sync_word(self):
        configurator = Cc1101Configurator()
        
        configurator.set_sync_word([0x01, 0x02])
        self.assertEqual(configurator._registers[addr.SYNC1:addr.SYNC0+1], [0x01, 0x02])
        self.assertEqual(configurator.get_sync_word(), [0x01, 0x02])
        

    def test_data_whitening_enable(self):
        configurator = Cc1101Configurator()
        
        configurator.set_data_whitening_enable(True)
        self.assertEqual(configurator._registers[addr.PKTCTRL0] & 0x40, 0x40)
        self.assertEqual(configurator.get_data_whitening_enable(), True)
        
        configurator.set_data_whitening_enable(False)
        self.assertEqual(configurator._registers[addr.PKTCTRL0] & 0x40, 0x00)
        self.assertEqual(configurator.get_data_whitening_enable(), False)

    def test_preamble_length_bytes(self):
        configurator = Cc1101Configurator()

        # Test valid preamble lengths
        for length in configurator._preamble_lengths:
            configurator.set_preamble_length_bytes(length)
            self.assertEqual((configurator._registers[addr.MDMCFG1] >> 4) & 0x07, configurator._preamble_lengths.index(length))
            self.assertEqual(configurator.get_preamble_length_bytes(), length)

        # Test invalid preamble length
        with self.assertRaises(ValueError):
            configurator.set_preamble_length_bytes(5)

    def test_packet_length_mode(self):
        configurator = Cc1101Configurator()

        for i in range(3):
            configurator.set_packet_length_mode(i)
            self.assertEqual(configurator._registers[addr.PKTCTRL0] & 0x03, i)
            self.assertEqual(configurator.get_packet_length_mode(), i)


    def test_packet_length(self):
        configurator = Cc1101Configurator()

        configurator.set_packet_length(0x12)
        self.assertEqual(configurator._registers[addr.PKTLEN], 0x12)
        self.assertEqual(configurator.get_packet_length(), 0x12)

        configurator.set_packet_length(0x34)
        self.assertEqual(configurator._registers[addr.PKTLEN], 0x34)
        self.assertEqual(configurator.get_packet_length(), 0x34)


    def test_crc_enable(self):
        configurator = Cc1101Configurator()

        configurator.set_crc_enable(True)
        self.assertEqual(configurator._registers[addr.PKTCTRL0] & 0x04, 0x04)
        self.assertEqual(configurator.get_crc_enable(), True)

        configurator.set_crc_enable(False)
        self.assertEqual(configurator._registers[addr.PKTCTRL0] & 0x04, 0x00)
        self.assertEqual(configurator.get_crc_enable(), False)


    def test_address_check_mode(self):
        configurator = Cc1101Configurator()

        for i in range(4):
            configurator.set_address_check_mode(i)
            self.assertEqual((configurator._registers[addr.PKTCTRL1]) & 0x03, i)
            self.assertEqual(configurator.get_address_check_mode(), i)


    def test_address(self):
        configurator = Cc1101Configurator()

        configurator.set_address(0x12)
        self.assertEqual(configurator._registers[addr.ADDR], 0x12)
        self.assertEqual(configurator.get_address(), 0x12)


    def test_crc_auto_flush(self):
        configurator = Cc1101Configurator()

        configurator.set_crc_auto_flush(True)
        self.assertEqual(configurator._registers[addr.PKTCTRL1] & 0x08, 0x08)
        self.assertEqual(configurator.get_crc_auto_flush(), True)

        configurator.set_crc_auto_flush(False)
        self.assertEqual(configurator._registers[addr.PKTCTRL1] & 0x08, 0x00)
        self.assertEqual(configurator.get_crc_auto_flush(), False)


    def test_append_status_enabled(self):
        configurator = Cc1101Configurator()

        configurator.set_append_status_enabled(True)
        self.assertEqual(configurator._registers[addr.PKTCTRL1] & 0x04, 0x04)
        self.assertEqual(configurator.get_append_status_enabled(), True)

        configurator.set_append_status_enabled(False)
        self.assertEqual(configurator._registers[addr.PKTCTRL1] & 0x04, 0x00)
        self.assertEqual(configurator.get_append_status_enabled(), False)


    def test_fec_enable(self):
        configurator = Cc1101Configurator()

        configurator.set_fec_enable(True)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x80, 0x80)
        self.assertEqual(configurator.get_fec_enable(), True)

        configurator.set_fec_enable(False)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x80, 0x00)
        self.assertEqual(configurator.get_fec_enable(), False)

    
    def test_GDOx_config(self):
        configurator = Cc1101Configurator()

        for i in range(2):
            configurator.set_GDOx_config(i, 0x12)
            self.assertEqual(configurator._registers[addr.IOCFG2+(2-i)] & 0x3F, 0x12)
            self.assertEqual(configurator.get_GDOx_config(i), 0x12)


    def test_modulation_format(self):
        configurator = Cc1101Configurator()

        for i in [0, 1, 2, 4, 7]:
            configurator.set_modulation_format(i)
            self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x70, i << 4)
            self.assertEqual(configurator.get_modulation_format(), i)

    def test_GDOx_inverted(self):
        configurator = Cc1101Configurator()

        for i in range(2):
            configurator.set_GDOx_inverted(i, True)
            self.assertEqual(configurator._registers[addr.IOCFG2+(2-i)] & 0x40, 0x40)
            self.assertEqual(configurator.get_GDOx_inverted(i), True)

            configurator.set_GDOx_inverted(i, False)
            self.assertEqual(configurator._registers[addr.IOCFG2+(2-i)] & 0x40, 0x00)
            self.assertEqual(configurator.get_GDOx_inverted(i), False)

    
    def test_manchester_encoding_enable(self):
        configurator = Cc1101Configurator()

        configurator.set_manchester_encoding_enable(True)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x08, 0x08)
        self.assertEqual(configurator.get_manchester_encoding_enable(), True)

        configurator.set_manchester_encoding_enable(False)
        self.assertEqual(configurator._registers[addr.MDMCFG2] & 0x08, 0x00)
        self.assertEqual(configurator.get_manchester_encoding_enable(), False)


    def test_deviation_hz(self):
        configurator = Cc1101Configurator()

        configurator.set_deviation_hz(5e3)
        self.assertEqual(configurator._registers[addr.DEVIATN], 0x14)
        self.assertEqual(int(configurator.get_deviation_hz()), 4760)

        configurator.set_deviation_hz(10e3)
        self.assertEqual(configurator._registers[addr.DEVIATN], 0x24)
        self.assertEqual(int(configurator.get_deviation_hz()), 9521)

        configurator.set_deviation_hz(58e3)
        self.assertEqual(configurator._registers[addr.DEVIATN], 0x51)
        self.assertEqual(int(configurator.get_deviation_hz()), 57128)

    def test_sample_1(self):
        configurator = Cc1101Configurator(preset=presets.rf_setting_sample_1)

        test_values = [
            # (get_method, set_method, expected_value, test_value)
            (configurator.get_base_frequency_hz, configurator.set_base_frequency_hz, 867999939, 433919830),
            (configurator.get_data_rate_baud, configurator.set_data_rate_baud, 1199, 115051),
            (configurator.get_receiver_bandwidth_hz, configurator.set_receiver_bandwidth_hz, 58036, 325000),
            (configurator.get_frequency_offset_compensation_setting, configurator.set_frequency_offset_compensation_setting, (0, 2, 1, 2), (0, 2, 0, 3)),
        ]

        for get_method, set_method, expected_value, test_value in test_values:
            # Test initial values
            self.assertEqual(get_method(), expected_value)
            # Test set and get
            if type(test_value) is tuple:
                set_method(*test_value)
            else:
                set_method(test_value)
            self.assertEqual(get_method(), test_value)
            # set back to initial value
            if type(test_value) is tuple:
                set_method(*expected_value)
            else:
                set_method(expected_value)
            # verify that nothing else changed
            self.assertEqual(configurator._registers, presets.rf_setting_sample_1["registers"])
        

if __name__ == '__main__':
    unittest.main()