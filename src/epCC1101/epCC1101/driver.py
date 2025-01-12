
from abc import abstractmethod
class Abstract_Driver:
    gdo0 = None
    gdo2 = None

    @abstractmethod
    def __init__(self, spi_bus:int=0, cs_pin:int=0, spi_speed_hz:int=55700, gdo0:int=23, gdo1:int=None, gdo2:int=None):
        pass

    @abstractmethod
    def read_byte(self, register:int):
        return 0
    
    @abstractmethod
    def read_status_register(self, register:int):
        return 0
    
    @abstractmethod
    def read_burst(self, register:int, length:int):
        return []
    
    @abstractmethod
    def command_strobe(self, register:int):
        pass

    @abstractmethod
    def write_burst(self, register:int, data:bytes):
        pass

    @abstractmethod
    def set_pin_mode(self, pin:int, mode:int):
        pass

    @abstractmethod
    def reset_pin_mode(self, pin:int):
        pass

    @abstractmethod
    def wait_for_edge(self, pin:int, edge:int, timeout:int=1000):
        pass

    @abstractmethod
    def read_gdo0(self):
        return 0
    
    @abstractmethod
    def read_gdo2(self):
        return 0
    
    @abstractmethod
    def asynchronous_serial_read(self, threshold_pin_number:int, data_pin_number:int, timeout_ms:int):
        return []
    
    @abstractmethod
    def asynchronous_serial_write(self, data_pin_number:int, baudrate:int, data):
        return []
    
    @abstractmethod
    def synchronous_serial_write(self, clock_pin_number:int, data_pin_number:int, data):
        return []