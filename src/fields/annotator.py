#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import numpy as np

from sklearn.preprocessing import normalize
from sklearn.svm import SVC

classes = [
    'FLAG',
    'NUMBER',
    'ASCII',
    'UNIFORM',
]

dns_structure = [3, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]

limit = 200
packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
msgs = [p.data[:limit] for p in packets]

lens = []
for msg in msgs:
    len_ = ord(msg[12])
    lens.append(len_)
median = np.median(lens)

dns_structure.extend((median - 1) * [2])
distributions = np.zeros((len(dns_structure), 256))
for msg in msgs:
    len_ = ord(msg[12])
    for i in range(min(13 + len_, len(dns_structure))):
        byte = ord(msg[i])
        distributions[i, byte] += 1
distributions = normalize(distributions, norm='l1', axis=1)

from string import printable
from scipy.stats import poisson
X = np.array((len(distributions), 5))
for dist in distributions:
    num_zero = len(np.where(dist == 0)[0])
    num_non_zero = 256 - num_zero
    num_ascii = sum([f for (b, f) in enumerate(dist) if b in map(ord, printable)])
    med = np.median(dist)
    deviation_uniform = sum([abs(f - med) for f in dist])
    deviation_poisson = float('inf')
    for mu in range(256):
        dev = sum(abs(dist[b] - poisson.pmf(b, mu)) for b in range(256))
        if dev < deviation_poisson:
            deviation_poisson = dev
    print num_zero, num_non_zero, num_ascii, deviation_uniform, deviation_poisson

X = normalize(X, norm='l1', axis=0)

clf = SVC(C=1.0, gamma=0.0, probability=True)
clf.fit(X, y)









#pred = clf.predict_proba(X)
#
#correct = 0
#for i in range(len(X)):
#    if np.argmax(pred[i]) == y[i]:
#        correct += 1
#print '%d correct out of %d (%.2f%%)' % (correct, len(X), 100 * correct / len(X))

#print classes_rev
#for i in range(40):
#    print pred[i], classes_rev[y[i]], names[i]


GP = np.zeros((limit, 256))
for msg in global_msgs:
    for (pos, val) in enumerate(msg):
        GP[pos,ord(val)] += 1
GP = normalize(GP, norm='l1', axis=0)

pred = clf.predict_proba(GP)
print classes_rev
print pred

