#! /usr/bin/env python

import align
import string
import numpy as np

s1 = '----01000001000000000000--------------------------------0000--0001'
s2 = '00010100000100000000000003646566036768690000010001'
s3 = '000201000001000000000000054344646566036768690000010001'
s4 = '000201000001000000000000054444646566036768690000010001'

def s2a(s):
    return map(lambda (c1, c2): 256 if c1 == '-' else int(c1 + c2, 16), zip(s[0::2], s[1::2]))

S_N = 3 * np.identity(257) - 1 * np.ones((257, 257))
S_N[256,:] = np.zeros(257)
S_N[:,256] = np.zeros(257)
S_N = S_N.astype(np.int16)

ascii_ = map(ord, string.printable)
S_A = -1 * np.ones((257, 257))
for i in ascii_:
    for j in ascii_:
        S_A[i,j] = 2
for i in range(256):
    S_A[i,i] = 2
S_A[256,:] = np.zeros(257)
S_A[:,256] = np.zeros(257)
S_A = S_A.astype(np.int16)

# Reverse the alignments to force gap insertion from the right
(_, a12_1, a12_2) = align.align(s2a(s1)[::-1], s2a(s2)[::-1], -1, S_A)
(_, a13_1, a13_3) = align.align(s2a(s1)[::-1], s2a(s3)[::-1], -1, S_A)
(_, a23_2, a23_3) = align.align(a12_2, a13_3, -1, S_A)

# Reverse the the alignments again to output them in the correct order
print align.alignment_to_string(a23_2[::-1], hex_=True)
print align.alignment_to_string(a23_3[::-1], hex_=True)

