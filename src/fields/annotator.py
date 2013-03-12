#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import numpy as np

from features import *
from itertools import chain
from sklearn.preprocessing import normalize
from sklearn.svm import SVC
from sklearn import grid_search

classes = [
    'CONSTANT',
    'NUMBER',
    'ASCII',
    'UNIFORM',
]

dns_structure = [3, 3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]

features = [ConstantFeature(), AsciiFeature(), UniformFeature(), NumberFeature()]

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

X = np.ndarray((len(distributions), 4))
for (i, dist) in enumerate(distributions):
    X[i] = list(chain.from_iterable([feature.get_values(dist) for feature in features]))
    #print num_zero, num_non_zero, num_ascii, deviation_uniform, deviation_poisson
    #if deviation_poisson < 0.6:
    #    import matplotlib.pyplot as plt
    #    plt.bar(range(256), dist, color='y', alpha=0.8)
    #    plt.bar(range(256), pmf[:,best_mu], color='b', alpha=0.6)
    #    plt.show()

#X = normalize(X, norm='l2', axis=0)
y = np.asarray(dns_structure)

# grid search first
parameters = {'kernel':['rbf'], 'gamma':np.linspace(0, 80, 100).tolist(), 'C':range(1, 41)}
svc = SVC(probability=True)
clf = grid_search.GridSearchCV(svc, parameters, cv=2)
clf.fit(X, y)
print clf.best_params_
print clf.best_estimator_

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
msgs = [p.data[:limit] for p in packets[:4000]]

distributions = np.zeros((limit, 256))
for msg in msgs:
    for i in range(min(len(msg), limit)):
        byte = ord(msg[i])
        distributions[i, byte] += 1
distributions = normalize(distributions, norm='l1', axis=1)

X = np.ndarray((len(distributions), 4))
for (i, dist) in enumerate(distributions):
    X[i] = list(chain.from_iterable([feature.get_values(dist) for feature in features]))
#X = normalize(X, norm='l2', axis=0)

pred = clf.predict_proba(X)

guesses = []
correct = 0
for i in range(len(X)):
    guess = np.argmax(pred[i])
    guesses.append(guess)
    #if guess == y[i]:
    #    correct += 1

#print '%d correct out of %d (%.2f%%)' % (correct, len(X), 100 * correct / len(X))
print classes
for i in range(18):
    print pred[i], classes[guesses[i]]#, classes[y[i]]

