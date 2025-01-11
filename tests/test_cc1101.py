import unittest
import sys
import os
sys.path.append(os.path.abspath('src/epCC1101'))

from epCC1101 import Driver, Cc1101, addresses as addr

class TestCc1101(unittest.TestCase):
    def setUp(self):
        self.driver = Driver(spi_bus=0, cs_pin=0)
        self.cc1101 = Cc1101(driver=self.driver)
        self.cc1101.reset()
    
    def test_get_chip_partnum(self):
        partnum = self.cc1101.get_chip_partnum()
        self.assertEqual(partnum, 0x00)

    def test_get_chip_version(self):
        version = self.cc1101.get_chip_version()
        self.assertIn(version, [0x04, 0x14])

    def test_default_configuration(self):
        self.assertEqual(self.cc1101.configurator.get_GDOx_config(2), 0x29)
        self.assertEqual(self.cc1101.configurator.get_GDOx_config(1), 0x2E)
        self.assertEqual(self.cc1101.configurator.get_GDOx_config(0), 0x3F)
        # todo: add more tests for the default configuration

    def test_get_marc_state_idle_after_reset(self):
        state = self.cc1101.get_marc_state()
        self.assertEqual(state, 0x01)

    def test_get_rssi_raw(self):
        self.cc1101.set_receive_mode()
        rssi = self.cc1101.get_rssi_raw()
        self.assertGreaterEqual(rssi, 0x00)
        self.assertLessEqual(rssi, 0xFF)

    def test_get_rssi_dbm(self):
        self.cc1101.set_receive_mode()
        rssi = self.cc1101.get_rssi_dbm()
        self.assertLessEqual(rssi, 0)
        self.assertGreaterEqual(rssi, -128)

    def test_get_configuration(self):
        registers, patable = self.cc1101.get_configuration()
        self.assertEqual(registers[0],  0x29)
        self.assertEqual(registers[1],  0x2e)
        self.assertEqual(registers[2],  0x3f)
        self.assertEqual(registers[3],  0x07)
        self.assertEqual(registers[4],  0xd3)
        self.assertEqual(registers[5],  0x91)
        self.assertEqual(registers[6],  0xff)
        self.assertEqual(registers[7],  0x04)
        self.assertEqual(registers[8],  0x45)
        self.assertEqual(registers[9],  0x00)
        self.assertEqual(registers[10], 0x00)
        self.assertEqual(registers[11], 0x0f)
        self.assertEqual(registers[12], 0x00)
        self.assertEqual(registers[13], 0x1e)
        self.assertEqual(registers[14], 0xc4)
        self.assertEqual(registers[15], 0xec)
        self.assertEqual(registers[16], 0x8c)
        self.assertEqual(registers[17], 0x22)
        self.assertEqual(registers[18], 0x02)
        self.assertEqual(registers[19], 0x22)
        self.assertEqual(registers[20], 0xf8)
        self.assertEqual(registers[21], 0x47)
        self.assertEqual(registers[22], 0x07)
        self.assertEqual(registers[23], 0x30)
        self.assertEqual(registers[24], 0x04)
        self.assertEqual(registers[25], 0x76)
        self.assertEqual(registers[26], 0x6c)
        self.assertEqual(registers[27], 0x03)
        self.assertEqual(registers[28], 0x40)
        self.assertEqual(registers[29], 0x91)
        self.assertEqual(registers[30], 0x87)
        self.assertEqual(registers[31], 0x6b)
        self.assertEqual(registers[32], 0xf8)
        self.assertEqual(registers[33], 0x56)
        self.assertEqual(registers[34], 0x10)
        self.assertEqual(registers[35], 0xa9)
        self.assertEqual(registers[36], 0x0a)
        self.assertEqual(registers[37], 0x20)
        self.assertEqual(registers[38], 0x0d)
        self.assertEqual(registers[39], 0x41)
        self.assertEqual(registers[40], 0x00)
        self.assertEqual(registers[41], 0x59)
        self.assertEqual(registers[42], 0x7f)
        self.assertEqual(registers[43], 0x3f)
        self.assertEqual(registers[44], 0x88)
        self.assertEqual(registers[45], 0x31)
        self.assertEqual(registers[46], 0x0b)

        self.assertEqual(patable[0], 0xc6)
        for i in range(1, 8):
            self.assertEqual(patable[i], 0x00)

    def test_set_idle_mode(self):
        self.cc1101.set_idle_mode()
        state = self.cc1101.get_marc_state()
        self.assertEqual(state, addr.MARCSTATE_IDLE)

    def test_set_receive_mode(self):
        self.cc1101.set_receive_mode()
        state = self.cc1101.get_marc_state()
        self.assertEqual(state, addr.MARCSTATE_RX)

    def test_set_transmit_mode(self):
        self.cc1101.set_transmit_mode()
        state = self.cc1101.get_marc_state()
        self.assertEqual(state, addr.MARCSTATE_TX)

    def test_transmit_fixed_length_mode_non_blocking_pass(self):
        self.cc1101.configurator.set_packet_length_mode(0)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        self.cc1101.transmit(data=bytes([0x00 for _ in range(10)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_blocking_pass(self):
        self.cc1101.configurator.set_packet_length_mode(0)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        self.cc1101.transmit(data=bytes([0x00 for _ in range(10)]), blocking=True)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_non_blocking_fail_1(self):
        self.cc1101.configurator.set_packet_length_mode(0)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        with self.assertRaises(ValueError):
            self.cc1101.transmit(data=bytes([0x00 for _ in range(11)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_non_blocking_fail_2(self):
        self.cc1101.configurator.set_packet_length_mode(0)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        with self.assertRaises(ValueError):
            self.cc1101.transmit(data=bytes([0x00 for _ in range(9)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_non_blocking_pass_1(self):
        self.cc1101.configurator.set_packet_length_mode(1)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        self.cc1101.transmit(data=bytes([0x00 for _ in range(10)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_non_blocking_pass_2(self):
        self.cc1101.configurator.set_packet_length_mode(1)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        self.cc1101.transmit(data=bytes([0x00 for _ in range(9)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_blocking_pass(self):
        self.cc1101.configurator.set_packet_length_mode(1)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        self.cc1101.transmit(data=bytes([0x00 for _ in range(10)]), blocking=True)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

    def test_transmit_fixed_length_mode_non_blocking_fail(self):
        self.cc1101.configurator.set_packet_length_mode(1)
        self.cc1101.configurator.set_packet_length(10)
        self.cc1101.set_configuration()
        with self.assertRaises(ValueError):
            self.cc1101.transmit(data=bytes([0x00 for _ in range(11)]), blocking=False)
        self.assertEqual(self.cc1101.get_marc_state(), addr.MARCSTATE_IDLE)

if __name__ == '__main__':
    unittest.main()
