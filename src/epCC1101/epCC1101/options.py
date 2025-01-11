

# see FOCCFG - Frequency Offset Compensation Configuration
FOC_BS_CS_GATE_OPTIONS = {
    0: "Always on",
    1: "Freeze until carrier sense is asserted"
}

# see FOCCFG - Frequency Offset Compensation Configuration
FOC_PRE_K_OPTIONS ={
    0: "K",
    1: "2K",
    2: "3K",
    3: "4K"
}         

# see FOCCFG - Frequency Offset Compensation Configuration
FOC_POST_K_OPTIONS = {
    0: "Same as FOC_PRE_K",
    1: "K/2"
}

# see FOCCFG - Frequency Offset Compensation Configuration
FOC_LIMIT = {
    0: "±0 No compensation",
    1: "±BW_CHAN/8",
    2: "±BW_CHAN/4",
    3: "±BW_CHAN/2"
}

BYTE_SYNCHRONIZATION_MODES = {
    0: "No preamble/sync",
    1: "15/16 sync word bits detected",
    2: "16/16 sync word bits detected",
    3: "30/32 sync word bits detected",
    4: "No preamble/sync, carrier-sense above threshold",
    5: "15/16 + carrier-sense above threshold",
    6: "16/16 + carrier-sense above threshold",
    7: "30/32 + carrier-sense above threshold"
}

# see PKTCTRL0 - Packet Automation Control
PAKET_LENGTH_OPTIONS = {
    0: "Fixed",
    1: "Variable",
    2: "Infinite"
}

# see PKTCTRL1 - Packet Automation Control
ADDRESS_CHECK_OPTIONS = {
    0: "No address check",
    1: "Address check, no broadcast",
    2: "Address check, 0 (0x00) broadcast",
    3: "Address check, 0 and 255 (0x00 and 0xFF) broadcast"
}

# see MDMCFG2 - Modem Configuration
MODULATION_FORMAT_OPTIONS = {
    0: "2-FSK",
    1: "GFSK",
    3: "ASK_OOK",
    4: "4-FSK",
    7: "MSK"
}