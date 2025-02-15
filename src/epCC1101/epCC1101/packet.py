from epCC1101.configurator import Cc1101Configurator

class Protocol:
    def __init__(self):
        self.base_frequency = 433.92e6
        self.data_rate = 1000
        self.modulation_format = 0

    @property
    def base_frequency(self) -> float:
        """Get or set the base frequency of the radio in Hz. The base frequency is the center frequency of the radio.
        """
        return self.base_frequency
    
    @base_frequency.setter
    def base_frequency(self, value: float):
        self.base_frequency = value

    @property
    def data_rate(self) -> int:
        """Get or set the data rate of the radio in baud. The data rate is the rate at which bits are transmitted.
        """
        return self.data_rate

    @data_rate.setter
    def data_rate(self, value: int):
        self.data_rate = value
    
    @property
    def modulation_format(self) -> int:
        """Get or set the modulation format of the radio.

        Accepted values:
            0: 2-FSK
            1: GFSK
            3: ASK/OOK
            4: 4-FSK
            7: MSK
        """
        return self.modulation_format
    
    @modulation_format.setter
    def modulation_format(self, value: int):
        assert self.modulation_format in [0, 1, 2, 3, 4], "Invalid modulation format."
        self.modulation_format = value

    def setup_configurator(self, configurator: Cc1101Configurator):
        configurator.set_base_frequency_hz(self.base_frequency)
        configurator.set_data_rate_baud(self.data_rate)
        configurator.set_modulation_format(self.modulation_format)

class Cc1101_Packet_Protocol(Protocol):
    def __init__(self):
        self.packet_length_mode = 0
        self.packet_length = 0
        self.receiver_address = 0

    @property
    def length_mode(self) -> int:
        """Get or set the length mode of the packet.

        Accepted values:
            0: Fixed packet length mode
            1: Variable packet length mode
            2: Infinite packet length mode
        """
        return self.length_mode
    
    @length_mode.setter
    def length_mode(self, value:int):
        assert self.packet_length_mode in [0, 1, 2], "Invalid packet length mode."
        self.packet_length_mode = value

    @property
    def packet_length(self) -> int:
        """Get or set the length of the packet. The length of the packet is the number of 
        payload bytes. Maximum value is 255.
        """
        return self.packet_length
    
    @packet_length.setter
    def packet_length(self, value: int):
        assert value <= 255, "Packet length is too long."
        self.packet_length = value

    @property
    def address_mode(self) -> int:
        """Get or set the address mode of the packet.

        Accepted values:
          0: No address check
          1: Address check
          2: Address check and 0 (0x00) broadcast
          3: Address check and 0 (0x00) and 255 (0xFF) broadcast
        """
        return self.address_mode
    
    @address_mode.setter
    def address_mode(self, value: int):
        assert self.address_mode in [0, 1, 2, 3], "Invalid address mode."
        self.address_mode = value

    @property
    def receiver_address(self) -> int:
        """Get or set the address of the receiver. The address is used to filter out packets.
        Must be a value between 0 and 255. 0 and 255 are used for broadcast.
        """
        return self.receiver_address
    
    @receiver_address.setter
    def receiver_address(self, value: int):
        assert 0 <= value <= 255, "Invalid receiver address."
        self.receiver_address = value

    def setup_configurator(self, configurator: Cc1101Configurator):
        super().setup_configurator(configurator)
        configurator.set_packet_format(0)
        configurator.set_packet_length_mode(self.packet_length_mode)
        configurator.set_packet_length(self.packet_length)
        configurator.set_address_check_mode(self.address_mode)
        configurator.set_address(self.receiver_address)


class PT2262_Protocol(Protocol):
    def __init__(self):
        self.base_frequency = 433.92e6
        self.data_rate = 2760
        self.modulation_format = 3

    def setup_configurator(self, configurator: Cc1101Configurator):
        super().setup_configurator(configurator)
        configurator.set_packet_format(1)
        configurator.set_base_frequency_hz(self.base_frequency)
        configurator.set_data_rate_baud(self.data_rate)
        configurator.set_modulation_format(self.modulation_format)


class Packet:
    def __init__(self):
        pass

    @property
    def protocol(self) -> Protocol:
        """Get or set the protocol of the packet.
        """
        return self._protocol
    
    @protocol.setter
    def protocol(self, value: Protocol):
        self._protocol = value


class TxPacket(Packet):
    def __init__(self):
        pass


class RxPacket(Packet):
    """Represents a received packet.
    """
    def __init__(self, timestamp:float):
        """Initializes a new instance of the RxPacket class.

        Args:
            timestamp (float): The timestamp, when the packet was received.
        """
        super().__init__()
        self._timestamp = timestamp


class NormalRxPacket(RxPacket):
    """Represents a received packet in normal mode.
    """
    def __init__(self, payload: list, length: int, rssi: int, lqi: int, crc_ok: int,
                 *args, **kwargs):
        """Initializes a new instance of the NormalRxPacket class.

        Args:
            payload (list): The payload of the packet.
            length (int): The length of the packet.
            rssi (int): The RSSI of the packet.
            lqi (int): The LQI of the packet.
            crc_ok (int): The CRC status of the packet.
            timestamp (float): The timestamp, when the packet was received.
        """
        super().__init__(*args, **kwargs)
        self._payload = payload
        self._length = length
        self._rssi = rssi
        self._lqi = lqi
        self._crc_ok = crc_ok

    def __repr__(self):
        return f"NormalRxPacket(payload={' '.join([f'{x:02x}' for x in self._payload])}, length={self._length}, rssi={self._rssi}, lqi={self._lqi}, crc_ok={self._crc_ok})"


class SyncRxPacket(RxPacket):
    """Represents a received packet in synchronous mode.
    """
    def __init__(self, bits: list, *args, **kwargs):
        """Initializes a new instance of the SyncRxPacket class.

        Args:
            bits (list): A list of bits of the packet.
            timestamp (float): The timestamp, when the packet was received.
        """
        super().__init__(*args, **kwargs)
        self._bits = bits

    def get_bitstream(self):
        """Returns the bitstream of the packet.
        """
        return self._bits
    
    def __repr__(self):
        return f"SyncRxPacket(bits={' '.join([f'{x:02x}' for x in self.get_bitstream()])})"


class AsyncRxPacket(RxPacket):
    """Represents a received packet in asynchronous mode.
    """
    def __init__(self, edges: list, *args, **kwargs):
        """Initializes a new instance of the AsyncRxPacket class.

        Args:
            edges (list): A list of tuples, where each tuple contains the 
              timestamp of the edge and the edge type.
            timestamp (float): The timestamp, when the packet was received.
        """
        super().__init__(*args, **kwargs)
        self._edges = edges

    def get_bitstream(self):
        """Returns the bitstream of the packet.
        """
        bitstream = []
        t_bit = 1/self.protocol.data_rate
        for i in range(1, len(self._edges)):
            pulse_length = self._edges[i][1] - self._edges[i-1][1]
            bit = self._edges[i][0]
            bitstream += [1-bit] * round(pulse_length / t_bit)
        return bitstream
    
    def __repr__(self):
        return f"AsyncRxPacket(edges={self._edges})"