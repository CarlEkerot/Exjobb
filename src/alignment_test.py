#! /usr/bin/env python

import pcap_reassembler
import align
import numpy

def score(a, b):
    if a == b:
        return 2
    return -1

def test():
    size = 100

    packets = pcap_reassembler.load_pcap('../dns-30628-packets.pcap')
    msgs = map(lambda x: x.data, packets[:size])

    S = numpy.ndarray((256, 256), dtype=numpy.int)
    for i in range(256):
        for j in range(256):
            S[i,j] = score(i, j)
    M = numpy.ndarray((size, size))
    for i in range(size):
        for j in range(size):
            (s, _, _) = align.align(msgs[i], msgs[j], -2, S, local=True)
            M[i,j] = s

    print(M)

test()
