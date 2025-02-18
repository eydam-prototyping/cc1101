import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import time
import multiprocessing

from epCC1101 import Cc1101, Driver, presets, SyncTxPacket, Princeton25bit_Protocol

# Create a driver object
driver_receiver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)
driver_transmitter = Driver(spi_bus=0, cs_pin=1, gdo0=22, gdo2=23)

# Create a CC1101 object
cc1101_transmitter = Cc1101(driver=driver_transmitter)
cc1101_transmitter.reset()
cc1101_transmitter.load_preset(presets.rf_setting_async_ask_ook)

cc1101_receiver = Cc1101(driver=driver_receiver)
cc1101_receiver.reset()
cc1101_receiver.load_preset(presets.rf_setting_async_ask_ook)

protocol = Princeton25bit_Protocol()

protocol.setup_configurator(cc1101_transmitter.configurator)
cc1101_transmitter.set_configuration()

protocol.setup_configurator(cc1101_receiver.configurator)
cc1101_receiver.set_configuration()

packet_number = 20
retransmissions = 5

done = False

def tansmitter_func():
    global done
    for i in range(packet_number):
        logger.info("Transmitting...")
        payload=protocol.get_physical_bytes({"address":0x1234, "data":i})
        packet = SyncTxPacket([0x00]*3 + payload + [0x00]*3)
        for _ in range(retransmissions):
            time.sleep(0.1)
            cc1101_transmitter.transmit(packet)
        time.sleep(1)
    done = True


def receiver_func():
    global done
    packets = []
    while not done:
        try:
            logger.info("Waiting for Packet...")
            packet = cc1101_receiver.receive(timeout_ms=10000, max_same_bits=4)
            logical_values = protocol.parse(packet.get_bitstream())
            if logical_values:
                logger.info(f"Address: {logical_values['address']:06x}, Data: {logical_values['data']:02x}")
                packets.append(logical_values)
            logger.info(packet)
        except Exception as e:
            logger.error(f"Error: {e}")
            break

    logger.info(f"Received {len(packets)} packets.")
    packet_numbers = {}
    for i, packet in enumerate(packets):
        logger.info(f"{i:2d} - Address: {packet['address']:06x}, Data: {packet['data']:02x}")
        if packet['data'] in packet_numbers:
            packet_numbers[packet['data']] += 1
        else:
            packet_numbers[packet['data']] = 1
    
    logger.info("========================================")
    logger.info("Results:")

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    for i in range(packet_number):
        if i in packet_numbers:
            logger.info(f"{GREEN}Packet {i:2d}: {packet_numbers[i]}{RESET}")
        else:
            logger.info(f"{RED}Packet {i:2d}: missing{RESET}")
    logger.info("========================================")

transmitter_thread = multiprocessing.Process(target=tansmitter_func)
receiver_thread = multiprocessing.Process(target=receiver_func)

receiver_thread.start()
transmitter_thread.start()
