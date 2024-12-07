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

## Meaning of Parameters

### Base Frequency

```python
cc1101.configurator.set_base_frequency_hz(433.92e6)
cc1101.set_configuration()
```
The base frequency is a key parameter in configuring the CC1101 transceiver, as it defines the central frequency at which the device operates. This parameter determines the starting point of the RF (radio frequency) signal generation and reception, which is crucial for ensuring compatibility with the chosen communication standard or regulatory requirements.

The base frequency is typically set in the range of 300 MHz to 928 MHz, depending on the hardware and regional regulations. For example, in the ISM (Industrial, Scientific, and Medical) bands, common frequencies include 433 MHz, 868 MHz, and 915 MHz.

*Note: Make sure, you have the right Antenna connected*

### Modulation Format

```python
# 0: 2-FSK
# 1: GFSK
# 3: ASK_OOK
# 4: 4-FSK
# 7: MSK
cc1101.configurator.set_modulation_format(0)
cc1101.set_configuration()
```
The modulation format determines how data is encoded onto the carrier frequency for transmission and decoded during reception. This parameter is essential for ensuring compatibility between transmitting and receiving devices, as both must use the same modulation scheme to communicate effectively.

The CC1101 supports several modulation formats, including:
  * 2/4-FSK (Frequency Shift Keying): A robust modulation scheme commonly used in environments with high interference.
  * GFSK (Gaussian Frequency Shift Keying): A variation of FSK with smoother transitions, reducing spectral bandwidth and interference.
  * ASK/OOK (Amplitude Shift Keying/On-Off Keying): Simple schemes often used in low-power, short-range applications like remote controls.
  * MSK (Minimum Shift Keying): Provides high spectral efficiency, ideal for data-intensive applications.

The choice of modulation format impacts key aspects of the communication, including data rate, power consumption, and signal robustness. For example, FSK is highly reliable in noisy environments, while OOK is energy-efficient but more susceptible to interference.

#### 2-FSK (2 Frequency Shift Keying)

2-FSK is a digital modulation scheme where the carrier frequency shifts between two discrete frequencies to represent binary data (0 and 1). It is one of the simplest forms of frequency modulation and is widely used for robust communication in environments with noise or interference.

**Relevant CC1101 Parameters:**

  * Deviation: The difference between the carrier frequency and the modulated frequencies.

![2-FSK Modulation](img/Sample_2-FSK.png)


#### 4-FSK (4 Frequency Shift Keying)

Like 2-FSK, but with 4 Frequencies.

![4-FSK Modulation](img/Sample_4-FSK.png)

#### ASK (Amplitude Shift Keying) / OOK (On-Off Keying)

ASK (Amplitude Shift Keying) is a modulation scheme where the amplitude of the carrier signal varies to represent binary data. Unlike OOK, which is a subset of ASK with only two states (presence or absence of a signal), ASK can include more amplitude levels for more complex data encoding, though in most applications, it uses only two states:

High Amplitude represents binary 1.
Low Amplitude (or Zero in OOK) represents binary 0.
ASK/OOK is commonly used in simple, low-power communication systems such as wireless sensors, keyless entry systems, and remote controls.

**Relevant CC1101 Parameters:**

  * PA-Table Setting: \
      Byte 0 represents the power for a logical zero\
      Byte 1 represents the power for a logical one

  * FREND0.PA_POWER represents the PA power setting, that is used for a logical one. Default is 1.

![ASK/OOK Modulation](img/Sample_ASK_OOK.png)