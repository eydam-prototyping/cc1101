
from epCC1101.driver import Abstract_Driver
import epCC1101.addresses as addr
class Driver(Abstract_Driver):
    gdo0 = None
    gdo2 = None
    chunk_size = 32
    fifo_rw_interval = 0.001

    _registers = [0x29, 0x2e, 0x3f, 0x07, 0xd3, 0x91, 0xff, 0x04, 0x45, 0x00, 0x00, 0x0f, 0x00, 0x1e, 0xc4, 0xec, 0x8c, 0x22, 0x02, 0x22, 0xf8, 0x47, 0x07, 0x30, 0x04, 0x76, 0x6c, 0x03, 0x40, 0x91, 0x87, 0x6b, 0xf8, 0x56, 0x10, 0xa9, 0x0a, 0x20, 0x0d, 0x41, 0x00, 0x59, 0x7f, 0x3f, 0x88, 0x31, 0x0b]
    _patable = [0xc6, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    _marcstate = addr.MARCSTATE_IDLE

    def __init__(self, spi_bus:int=0, cs_pin:int=0, spi_speed_hz:int=55700, gdo0:int=23, gdo1:int=None, gdo2:int=None):
        pass

    def read_byte(self, register:int):
        return 0
    
    def read_status_register(self, register:int):
        if register == addr.PARTNUM:
            return 0x00
        if register == addr.VERSION:
            return 0x04
        if register == addr.RSSI:
            return 0x30
        if register == addr.MARCSTATE:
            return self._marcstate
        return 0
    
    def read_burst(self, register:int, length:int):
        if register == addr.PATABLE:
            return self._patable[0:length]
        else:
            return self._registers[register:register+length]
    
    def command_strobe(self, register:int):
        if register == addr.SIDLE:
            self._marcstate = addr.MARCSTATE_IDLE
        if register == addr.STX:
            self._marcstate = addr.MARCSTATE_TX
        if register == addr.SRX:
            self._marcstate = addr.MARCSTATE_RX

    def write_burst(self, register:int, data:bytes):
        if register == addr.PATABLE:
            self._patable[0:len(data)] = data
        elif register == addr.TXFIFO:
            self._marcstate = addr.MARCSTATE_IDLE
        else:
            self._registers[register:register+len(data)] = data

    def wait_for_edge(self, pin:int, edge:int, timeout:int=1000):
        pass

    def read_gdo0(self):
        return 0
    
    def read_gdo2(self):
        return 0
    
    def asynchronous_serial_read(self, threshold_pin_number:int, data_pin_number:int, timeout_ms:int):
        return []
    
    def asynchronous_serial_write(self, data_pin_number:int, baudrate:int, data):
        return []
    
    def synchronous_serial_write(self, clock_pin_number:int, data_pin_number:int, data):
        return []