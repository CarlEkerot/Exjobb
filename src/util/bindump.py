#! /usr/bin/env python

import sys

def hex_to_bin(s):
    assert(len(s) % 2 == 0)
    line = ""
    for i in range(0, len(s), 2):
        if i != 0 and i % 8 == 0:
            line += '\n'
        byte = s[i] + s[i+1]
        bin_byte = int(bin(int(byte, 16))[2:])
        line += '%08d ' % bin_byte
    return line

print(hex_to_bin(sys.argv[1]))
