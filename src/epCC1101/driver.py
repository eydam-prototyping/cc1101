
from abc import ABC, abstractmethod
class Abstract_Driver:
    gdo0 = None
    gdo2 = None

    @abstractmethod
    def __init__(self):
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
    def wait_for_edge(self, pin:int, edge:int, timeout:int=1000):
        pass

    @abstractmethod
    def read_gdo0(self):
        return 0
    
    @abstractmethod
    def read_gdo2(self):
        return 0
    
    @abstractmethod
    def serial_read(self, gdo0:int, gdo2:int, timeout_ms:int):
        return []