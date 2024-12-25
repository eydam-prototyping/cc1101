from epCC1101.cc1101 import Raw_Received_Packet

class Interpreted_Packet:
    def __init__(self, raw_packet:Raw_Received_Packet):
        self.raw_packet = raw_packet
        self.tmean = self.estimate_bit_length()
        self.bits = self.calc_bits(self.tmean)

    def estimate_bit_length(self):
        assert len(self.raw_packet.edges) > 20, "Packet is too short to estimate bit length"
        sorted_puls_length = [[], []]

        for i in range(1, len(self.raw_packet.edges)):
            sorted_puls_length[self.raw_packet.edges[i][0]].append(self.raw_packet.edges[i][1] - self.raw_packet.edges[i-1][1])
        
        sorted_puls_length = [
            sorted(sorted_puls_length[0]),
            sorted(sorted_puls_length[1])
        ]

        tmin = [
            sum(sorted_puls_length[0][0:5])/5,
            sum(sorted_puls_length[1][0:5])/5
        ]

        t1_cand = [
            [x for x in sorted_puls_length[0] if x <= tmin[0]*1.5],
            [x for x in sorted_puls_length[1] if x <= tmin[1]*1.5]
        ]

        tmean = [
            sum(t1_cand[0])/len(t1_cand[0]),
            sum(t1_cand[1])/len(t1_cand[1])
        ]

        return tmean
    
    def calc_bits(self, tmean):
        bits = []
        for i in range(1, len(self.raw_packet.edges)):
            pulse_length = self.raw_packet.edges[i][1] - self.raw_packet.edges[i-1][1]
            bit = self.raw_packet.edges[i][0]
            bits += [1-bit] * round(pulse_length / tmean[bit])
        return bits