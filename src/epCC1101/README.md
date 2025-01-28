# epCC1101

## General

The CC1101 is a cost-effective and energy-efficient RF transceiver from Texas Instruments. It supports various frequency bands (including 315 MHz, 433 MHz, 868 MHz, 915 MHz), multiple modulation schemes, and flexible configuration options.

Key features:
- Low power consumption in receive and transmit mode
- Supported frequency bands: 300–348 MHz, 387–464 MHz, 779–928 MHz
- Programmable data rate: up to 500 kBaud (depending on modulation and filter settings)
- Multiple modulation modes (2-FSK, GFSK, ASK/OOK, 4-FSK, MSK)
- Internal packet processing (Preamble, Sync Word, address check, CRC check)
- Configurable via SPI interface

Project goal:

In this repository, we provide functions and examples to control the CC1101 using a common platform (e.g., Arduino, ESP32, or other MCUs). The library abstracts SPI register accesses and offers convenient methods to quickly set up wireless communication.

## Usage

### Hardware Wiring

The CC1101 is connected to the microcontroller via an SPI interface. Typically, the following pins are used:
- MOSI (Master Out Slave In)
- MISO (Master In Slave Out)
- SCK (SPI Clock)
- CSN (Chip Select)
- Additionally, possibly GDO0 or GDO2 for interrupt or status signals.

### Software Initialization

After integrating the library, initialize the SPI interface and the CC1101-specific registers. You can use preconfigured register sets (SmartRF Studio from TI or your own settings) to configure the radio module for the desired frequency, data rate, and modulation.

```python
from epCC1101 import Cc1101, Driver, presets

driver = Driver(spi_bus=0, cs_pin=0, gdo0=5, gdo2=6)
cc1101 = Cc1101(driver=driver)
cc1101.reset()
```

## Packet Format

The CC1101 allows flexible design of packets. The formats can broadly be divided into Packet Mode, Synchronous Serial Mode, and Asynchronous Serial Mode.

### Packet Mode

In Packet Mode, the CC1101 automatically handles the generation of the Preamble, Sync Word, CRC, and optionally Addressing. Reception and verification of these fields also largely happen in the background. The RX and TX FIFOs are used for this.

#### Packet Structure

A typical packet structure in Packet Mode is shown below:

| Block     | Optional | Length	      | Meaning   |
|-----------|----------|--------------|-----------|
| Preamble  | No	   | 2 – 24 bytes | Used for receiver synchronization (bit sync) |
| Sync Word | No	   | 2 bytes	  | Marks the start of a valid data packet (byte sync) |
| Length	| Yes	   | 1 byte	      | Defines the payload length to be received (unless using fixed or infinite length) |
| Address	| Yes	   | 1 byte	      | Can be used for addressing |
| Payload	| No	   | Variable     | User data |
| CRC	    | Yes	   | 1 byte	      | Checksum for error detection |

#### Synchronous Serial Mode

In Synchronous Serial Mode, data is sent or received bit by bit via the GDOx pins, with the CC1101 functioning as the frequency synthesizer and modulator/demodulator. A synchronous clock line (usually via GDO) is used to clock the bits.

Advantages:
- Manual control over the data stream.
- Suitable for systems that want to implement their own packet structure.

Disadvantages:
- Higher software complexity, because all packet fields (preamble, sync, CRC) must be handled manually.

#### Asynchronous Serial Mode

In Asynchronous Serial Mode, the CC1101 outputs the modulated data on one of the GDOx pins as a continuous data stream or receives it (in FM modes). This is similar to a UART-like communication but without a clock line.

Advantages:
- Useful for simple OOK/ASK applications.
- Quick integration into existing serial protocols.

Disadvantages:
- Synchronization and packet creation are entirely the user’s responsibility.

## Frequency Settings

The following sections describe the frequency configuration options.

### Base Frequency
The base frequency is the carrier signal frequency and must lie within 300–348 MHz, 387–464 MHz, or 779–928 MHz.

### Frequency Deviation
The frequency deviation describes the offset for FSK modulation. A larger deviation increases the signal bandwidth but can improve interference immunity.

### Receiver Bandwidth
The receiver bandwidth. A narrower filter reduces noise but can lead to data loss if the deviation or frequency offset is too large.

### Channel Spacing
When multiple channels are used, the channel spacing defines the distance between individual channels.

## Modulation Formats
The CC1101 supports several modulation methods. Possible register values include:

0x00: 2-FSK
0x01: GFSK
0x03: ASK/OOK
0x04: 4-FSK
0x07: MSK

### 2-FSK – Frequency Shift Keying

- Frequency Shift Keying with two frequency states (Mark/Space).
- Easy to implement and robust.
- Good range at low baud rates.

### GFSK – Gaussian Frequency Shift Keying

- A smoothed variant of FSK.
- Reduces out-of-band emissions and improves spectral efficiency.

### ASK/OOK – Amplitude Shift Keying / On-Off Keying

- Particularly suitable for very simple protocols (e.g., remote controls, doorbells).
- Energy-saving because very little power is transmitted in the “Off” state.

### 4-FSK

- An extension of 2-FSK, featuring four frequency states.
- Enables higher data rates in the same frequency band but with increased complexity.

### MSK – Minimum Shift Keying

- A special FSK variant with minimal frequency deviation.
- Continuous phase transitions for highly efficient spectrum usage.