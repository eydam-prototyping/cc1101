import unittest


from epCC1101 import Driver, Cc1101

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

if __name__ == '__main__':
    unittest.main()
