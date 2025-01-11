import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from epCC1101 import Cc1101, Driver, presets

def main():
    parser = argparse.ArgumentParser(description="CC1101 CLI Tool")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-commands")

    driver_parser = argparse.ArgumentParser(add_help=False)
    driver_parser.add_argument(
        "--spi-bus", type=int, default=0, 
        help="SPI bus number (default: %(default)s)")
    
    driver_parser.add_argument(
        "--cs-pin", type=int, default=0, 
        help="CS pin number (default: %(default)s)")
    
    driver_parser.add_argument(
        "--spi-speed-hz", type=int, default=55700, 
        help="SPI speed in Hz (default: %(default)s)")
    
    driver_parser.add_argument(
        "--gdo0", type=int, default=23, 
        help="GDO0 pin number (default: %(default)s)")
    
    driver_parser.add_argument(
        "--log-level", type=str, default="INFO",
        help="Log level (default: %(default)s)")

    base_settings_parser = argparse.ArgumentParser(add_help=False)
    base_settings_parser.add_argument(
        "-p", "--preset", type=str, default="rf_setting_dr5k7_dev5k2_2fsk_rxbw58k",
        help="Preset configuration to load (default: %(default)s)")
    base_settings_parser.add_argument(
        "-f", "--base_frequency", type=int, 
        help="Base frequency in Hz (e.g. 433.92e6)")   
    base_settings_parser.add_argument(
        "-r", "--data_rate", type=int,
        help="Data rate in baud (e.g. 5700)")
    base_settings_parser.add_argument(
        "-m", "--modulation_format", type=int,
        help="Modulation format (e.g. 0 = 2-FSK, 1 = GFSK, 3 = ASK/OOK, 4 = 4-FSK, 7 = MSK)")
    base_settings_parser.add_argument(
        "-d", "--deviation", type=int,
        help="Frequency deviation in Hz")
    base_settings_parser.add_argument(
        "-s", "--sync_mode", type=int,
        help="Sync mode (e.g. 5 = 15/16 + carrier-sense above threshold, see datasheet for more)")
    

    send_parser = subparsers.add_parser("send", help="Sends a mesaage via CC1101", parents=[driver_parser, base_settings_parser])
    recv_parser = subparsers.add_parser("recv", help="Receives a mesaage via CC1101", parents=[driver_parser, base_settings_parser])

    send_parser.add_argument("message", type=str, help="Message to send")

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    driver = None

    if args.command in ["send", "recv"]:
        driver = setup_driver(args)

    cc1101 = Cc1101(driver=driver)
    cc1101.reset()

    if args.command == "send":
        setup_base_settings(args, cc1101)
        logger.info(f"Sending message: {args.message}")
        cc1101.transmit(bytes(args.message, "utf-8"))

def setup_driver(args):
    from epCC1101.rpi_driver import Driver
    return Driver(spi_bus=args.spi_bus, cs_pin=args.cs_pin, spi_speed_hz=args.spi_speed_hz, gdo0=args.gdo0)

def setup_base_settings(args, cc1101):

    if hasattr(presets, args.preset):
        logger.info(f"Loading preset: {args.preset}")
        preset = getattr(presets, args.preset)
        cc1101.load_preset(preset)
    else:
        logger.warning(f"Preset {args.preset} not found. Using default settings.")
        cc1101.get_configuration()

    if args.base_frequency is not None:
        logger.info(f"Setting base frequency: {args.base_frequency}")
        cc1101.configurator.set_base_frequency_hz(args.base_frequency)

    if args.data_rate is not None:
        logger.info(f"Setting data rate: {args.data_rate}")
        cc1101.configurator.set_data_rate_baud(args.data_rate)
    
    if args.modulation_format is not None:
        logger.info(f"Setting modulation format: {args.modulation_format}")
        cc1101.configurator.set_modulation_format(args.modulation_format)
    
    if args.deviation is not None:
        logger.info(f"Setting frequency deviation: {args.deviation}")
        cc1101.configurator.set_deviation_hz(args.deviation)

    if args.sync_mode is not None:
        logger.info(f"Setting sync mode: {args.sync_mode}")
        cc1101.configurator.set_sync_mode(args.sync_mode)

    cc1101.set_configuration()