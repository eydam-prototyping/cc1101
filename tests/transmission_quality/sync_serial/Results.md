# Test Results

| Key    | Value                                    |
|--------|------------------------------------------|
| Date   |                               18.02.2025 |
| Commit | 84d16542a19e82f788abb6a96cc86a8bcf6b33cf |
| Board  |                           pcb_cc1101_rpi |

## Test: test_princeton25bit_1.py

Description: Send packets and count, how many packets are successfully received.

| Key                        | Value   |
|----------------------------|---------|
| Number of Packets          |  20     |
| Repetitions of each Packet |   5     |
| Delay between Repetitions  |   1 s   |
| Delay between Packets      |   0.1 s |

```
INFO:__main__:========================================
INFO:__main__:Results:
INFO:__main__:Packet  0: 3
INFO:__main__:Packet  1: 3
INFO:__main__:Packet  2: 1
INFO:__main__:Packet  3: missing
INFO:__main__:Packet  4: 3
INFO:__main__:Packet  5: 4
INFO:__main__:Packet  6: 4
INFO:__main__:Packet  7: 1
INFO:__main__:Packet  8: 4
INFO:__main__:Packet  9: 3
INFO:__main__:Packet 10: 1
INFO:__main__:Packet 11: 4
INFO:__main__:Packet 12: 4
INFO:__main__:Packet 13: 1
INFO:__main__:Packet 14: 3
INFO:__main__:Packet 15: 2
INFO:__main__:Packet 16: 2
INFO:__main__:Packet 17: 1
INFO:__main__:Packet 18: 4
INFO:__main__:Packet 19: 1
INFO:__main__:========================================
```