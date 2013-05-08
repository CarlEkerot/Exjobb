#! /usr/bin/env python

import pcap_reassembler
import numpy as np
import matplotlib.pyplot as plt

from align import string_to_alignment

def _get_value_from_bytes(data):
    value = 0
    for byte in data:
        value = (value << 8) + byte
    return value

packets = pcap_reassembler.load_pcap('../cap/smb-only.cap', strict=True)
msgs = [string_to_alignment(p.payload) for p in packets]

from ransac import LineModel, ransac
_model = LineModel()
"""
X = [_get_value_from_bytes(msg[0:4]) for msg in msgs]
Y = [len(msg) for msg in msgs]
data = np.asarray([X, Y]).T

(params, _, res) = ransac(data, _model, 2, 0.5, 100)
k = params[0]
m = params[1]

plt.plot(X, Y, 'ko')
X = np.asarray([0, max(X)])
Y = params[0] * X + params[1]
plt.plot(X, Y, 'g-', linewidth=2)
plt.xlim(0, 400)
plt.ylim(0, 400)
plt.show()
"""
X = [msg[36] for msg in msgs]
Y = [len(msg) for msg in msgs]
data = np.asarray([X, Y]).T

(params, _, res) = ransac(data, _model, 2, 0.5, 100)
k = params[0]
m = params[1]

# plt.plot(X, Y, 'bo', edgecolor='b')
plt.scatter(X, Y, s=30, facecolor='b', lw=0)
X = np.asarray([0, max(X)])
Y = params[0] * X + params[1]
print params
plt.plot(X, Y, 'k-', linewidth=2)
plt.xlim(0, 50)
plt.ylim(39, 139)
plt.xlabel("Byte value")
plt.ylabel("Message length")
plt.show()

