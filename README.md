# CC1101 Driver for Raspberry Pi and Micropython

This project provides a Python driver for the CC1101 transceiver chip, enabling seamless integration with Raspberry Pi and other compatible platforms. The driver supports data transmission and reception, making it ideal for wireless communication projects.

## Usage
* Connect the CC1101 module to your hardware as per your wiring setup.

* Run a sample script:

    * For transmission:
        ```bash
        python samples/transmitter.py
        ```
    * For reception:
        ```bash
        python samples/receiver.py
        ```

## Project Structure
* **src/:** Contains the main driver code.
* **samples/**: Example scripts for transmission and reception.
* **tests/**: Unit tests for the driver.