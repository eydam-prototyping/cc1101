# Samples

## Transmitter

The `transmitter.py` file is a sample script designed to demonstrate the transmission functionality of the CC1101 chip. It provides users with a straightforward implementation to test the transmission capabilities using the CC1101 driver.

**Steps:**
  * Create a driver object, specify SPI settings and GDO0 Pin\
    *Note: don't change the functionality of the GDO0 Pin or otherwise the script won't work*

  * Create a CC1101 object and hand over the driver object

  * Reset the chip to get default settings

  * Load a preset, you could also create one by yourself

  * Change some settings as you like. Make sure to write the settings to the chip

  * Print the description

  * Send Messages

**Output:**

```log
INFO:rpi_driver:Initializing SPI device on bus 0, cs_pin 1, spi_speed_hz 55700
INFO:cc1101:Initializing CC1101 device
INFO:configurator:12   Data rate: 5.703 kbps
INFO:configurator:13   Receiver bandwidth: 101.562 kHz
INFO:configurator:14.1 Frequency offset compensation setting:
INFO:configurator:     FOC_BS_CS_GATE: 1 (Freeze until carrier sense is asserted)
INFO:configurator:     FOC_PRE_K: 2 (3K)
INFO:configurator:     FOC_POST_K: 1 (K/2)
INFO:configurator:     FOC_LIMIT: 2 (±BW_CHAN/4)
INFO:configurator:14.3 Byte synchronization mode: 5 (15/16 + carrier-sense above threshold)
INFO:configurator:14.3 Synchronization word: 0xD34B
INFO:configurator:15.1 Data whitening: 0
INFO:configurator:15.2 Preamble length: 2 bytes
INFO:configurator:     Packet length mode: 1 (Variable)
INFO:configurator:     Packet length: 255 bytes
INFO:configurator:     CRC enabled: 0
INFO:configurator:     Address check mode: 0 (No address check)
INFO:configurator:     Address: 0
INFO:configurator:15.3 CRC auto flush: 0
INFO:configurator:     Append status: 1
INFO:configurator:15.4 FEC enabled: 0
INFO:configurator:15.5 GDO0 configuration: 0x06
INFO:configurator:     GDO1 configuration: 0x2E
INFO:configurator:     GDO2 configuration: 0x29
INFO:configurator:     GDO0 inverted: 0
INFO:configurator:     GDO1 inverted: 0
INFO:configurator:     GDO2 inverted: 0
INFO:configurator:16   Modulation format: 0 (2-FSK)
INFO:configurator:     Manchester encoding: 0
INFO:configurator:16.1 Frequency deviation: 31.738 kHz
INFO:configurator:21   Base frequency: 433.920 MHz
INFO:__main__:Transmitting...
INFO:cc1101:Transmitting data b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7'
...
```

## Receiver
The `receiver.py` file is a sample script designed to demonstrate the reception functionality of the CC1101 chip. It provides a practical implementation for users to test the reception capabilities of the CC1101 driver.

**Steps:**
Same as for Transmitter

**Output:**
```log
INFO:rpi_driver:Initializing SPI device on bus 0, cs_pin 0, spi_speed_hz 55700
INFO:cc1101:Initializing CC1101 device
INFO:configurator:12   Data rate: 5.703 kbps
...

INFO:__main__:Waiting for Packet...
INFO:cc1101:Receiving data
INFO:__main__:Received_Packet(payload=b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7', length=199, rssi=46, lqi=10, crc_ok=True)
INFO:__main__:01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 30 31 32 33 34 35 36 37 38 39 3a 3b 3c 3d 3e 3f 40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 50 51 52 53 54 55 56 57 58 59 5a 5b 5c 5d 5e 5f 60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f 70 71 72 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f 80 81 82 83 84 85 86 87 88 89 8a 8b 8c 8d 8e 8f 90 91 92 93 94 95 96 97 98 99 9a 9b 9c 9d 9e 9f a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 aa ab ac ad ae af b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 ba bb bc bd be bf c0 c1 c2 c3 c4 c5 c6 c7
...
```