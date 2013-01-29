#! /usr/bin/env python

import pcap_reassembler
import align
import numpy

size = 10

packets = pcap_reassembler.load_pcap('../dns-30628-packets.pcap')
msgs = map(lambda x: x.data, packets[:size])

def S(a, b):
    if a == b:
        return 2
    return -1

M = numpy.ndarray((size, size))
for i in range(size):
    print i
    for j in range(size):
        (_, _, s) = align.align(msgs[i], msgs[j], -2, S, local=True)
        M[i,j] = s

print(M)

