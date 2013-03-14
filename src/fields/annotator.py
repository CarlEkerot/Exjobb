#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import pickle
import numpy as np

from features import *
from itertools import chain

CONSTANT    = 0
FLAG        = 1
ASCII       = 2
UNIFORM     = 3
NUMBER      = 4
UNKNOWN     = 5

classes = [
    'CONSTANT',
    'FLAG',
    'ASCII',
    'UNIFORM',
    'NUMBER',
    'UNKNOWN',
]

feature_functions = [
    ConstantFeature(),
    FlagFeature(),
    AsciiFeature(),
    UniformFeature(),
    NumberFeature()
]

def classify(features):
    if features[CONSTANT]:
        return CONSTANT
    if features[FLAG] < 8:
        return FLAG
    if features[ASCII] > 0.6:
        return ASCII
    if features[UNIFORM] < 0.4:
        return UNIFORM
    if features[NUMBER] < 1.2:
        return NUMBER
    else:
        return UNKNOWN

limit = 40
packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
with open('/media/data/dns-filtered/dns-30000-100-200-0.75-0.40.dump') as f:
    result = pickle.load(f)
cluster = result[5]
msgs = [p.data[:limit] for p in [packets[i] for i in cluster]]

distributions = np.zeros((limit, 256))
for msg in msgs:
    for (i, byte) in enumerate(msg):
        byte = ord(byte)
        distributions[i,byte] += 1

predictions = []
for (i, dist) in enumerate(distributions):
    features = list(chain.from_iterable([func.get_values(dist) for func in feature_functions]))
    class_ = classify(features)
    predictions.append((features, class_))

for (features, class_) in predictions:
    print features, classes[class_]

