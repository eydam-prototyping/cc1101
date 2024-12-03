# see "Table 43: Configuration Registers Overview"
# Configuration Registers
IOCFG2 = 0x00  # GDO2 output pin configuration
IOCFG1 = 0x01  # GDO1 output pin configuration
IOCFG0 = 0x02  # GDO0 output pin configuration
FIFOTHR = 0x03  # RX FIFO and TX FIFO thresholds
SYNC1 = 0x04  # Sync word, high byte
SYNC0 = 0x05  # Sync word, low byte
PKTLEN = 0x06  # Packet length
PKTCTRL1 = 0x07  # Packet automation control
PKTCTRL0 = 0x08  # Packet automation control
ADDR = 0x09  # Device address
CHANNR = 0x0A  # Channel number
FSCTRL1 = 0x0B  # Frequency synthesizer control
FSCTRL0 = 0x0C  # Frequency synthesizer control
FREQ2 = 0x0D  # Frequency control word, high byte
FREQ1 = 0x0E  # Frequency control word, middle byte
FREQ0 = 0x0F  # Frequency control word, low byte
MDMCFG4 = 0x10  # Modem configuration
MDMCFG3 = 0x11  # Modem configuration
MDMCFG2 = 0x12  # Modem configuration
MDMCFG1 = 0x13  # Modem configuration
MDMCFG0 = 0x14  # Modem configuration
DEVIATN = 0x15  # Modem deviation setting
MCSM2 = 0x16  # Main Radio Control State Machine configuration
MCSM1 = 0x17  # Main Radio Control State Machine configuration
MCSM0 = 0x18  # Main Radio Control State Machine configuration
FOCCFG = 0x19  # Frequency Offset Compensation configuration
BSCFG = 0x1A  # Bit Synchronization configuration
AGCTRL2 = 0x1B  # AGC control
AGCTRL1 = 0x1C  # AGC control
AGCTRL0 = 0x1D  # AGC control
WOREVT1 = 0x1E  # High byte Event 0 timeout
WOREVT0 = 0x1F  # Low byte Event 0 timeout
WORCTRL = 0x20  # Wake On Radio control
FREND1 = 0x21  # Front end RX configuration
FREND0 = 0x22  # Front end TX configuration
FSCAL3 = 0x23  # Frequency synthesizer calibration
FSCAL2 = 0x24  # Frequency synthesizer calibration
FSCAL1 = 0x25  # Frequency synthesizer calibration
FSCAL0 = 0x26  # Frequency synthesizer calibration
RCCTRL1 = 0x27  # RC oscillator configuration
RCCTRL0 = 0x28  # RC oscillator configuration
FSTEST = 0x29  # Frequency synthesizer calibration control
PTEST = 0x2A  # Production test
AGCTEST = 0x2B  # AGC test
TEST2 = 0x2C  # Various test settings
TEST1 = 0x2D  # Various test settings
TEST0 = 0x2E  # Various test settings

# Status registers
PARTNUM = 0x30  # Part number for CC1101
VERSION = 0x31  # Current version number
FREQEST = 0x32  # Frequency Offset Estimate
LQI = 0x33  # Demodulator estimate for Link Quality
RSSI = 0x34  # Received signal strength indication
MARCSTATE = 0x35  # Control state machine state
WORTIME1 = 0x36  # High byte of WOR timer
WORTIME0 = 0x37  # Low byte of WOR timer
PKTSTATUS = 0x38  # Current GDOx status and packet status
VCO_VC_DAC = 0x39  # Current setting from PLL calibration module
TXBYTES = 0x3A  # Underflow and number of bytes in the TX FIFO
RXBYTES = 0x3B  # Overflow and number of bytes in the RX FIFO
RCCTRL1_STATUS = 0x3C  # Last RC oscillator calibration result
RCCTRL0_STATUS = 0x3D  # Last RC oscillator calibration result

# FIFO access
RXFIFO = 0x3F  # Read access to the RX FIFO
TXFIFO = 0x3F  # Write access to the TX FIFO

# PATABLE values
PATABLE = 0x3E

# Command strobes
SRES = 0x30
SFSTXON = 0x31
SXOFF = 0x32
SCAL = 0x33
SRX = 0x34
STX = 0x35
SIDLE = 0x36
SWOR = 0x38
SPWD = 0x39
SFRX = 0x3A
SFTX = 0x3B
SWORRST = 0x3C
SNOP = 0x3D

# SPI Mask for register read/write
SPI_READ_MASK = 0x80
SPI_WRITE_MASK = 0x00
SPI_READ_BURST_MASK = SPI_READ_MASK | 0x40
SPI_WRITE_BURST_MASK = SPI_WRITE_MASK | 0x40

# MARC states
MARCSTATE_SLEEP = 0x00
MARCSTATE_IDLE = 0x01
MARCSTATE_XOFF = 0x02
MARCSTATE_VCOON_MC = 0x03
MARCSTATE_REGON_MC = 0x04
MARCSTATE_MANCAL = 0x05
MARCSTATE_VCOON = 0x06
MARCSTATE_REGON = 0x07
MARCSTATE_STARTCAL = 0x08
MARCSTATE_BWBOOST = 0x09
MARCSTATE_FS_LOCK = 0x0A
MARCSTATE_IFADCON = 0x0B
MARCSTATE_ENDCAL = 0x0C
MARCSTATE_RX = 0x0D
MARCSTATE_RX_END = 0x0E
MARCSTATE_RX_RST = 0x0F
MARCSTATE_TXRX_SWITCH = 0x10
MARCSTATE_RXFIFO_OVERFLOW = 0x11
MARCSTATE_FSTXON = 0x12
MARCSTATE_TX = 0x13
MARCSTATE_TX_END = 0x14
MARCSTATE_RXTX_SWITCH = 0x15
MARCSTATE_TXFIFO_UNDERFLOW = 0x16
