#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import pickle
import align
import string
import numpy as np

from features import *
from itertools import chain

CONSTANT    = 0
FLAG        = 1
ASCII       = 2
UNIFORM     = 3
NUMBER      = 4
UNKNOWN     = 5
VARIABLE    = 6

classes = [
    'CONSTANT',
    'FLAG',
    'ASCII',
    'UNIFORM',
    'NUMBER',
    'UNKNOWN',
    'VARIABLE',
]

feature_functions = [
    ConstantFeature(),
    FlagFeature(),
    AsciiFeature(),
    UniformFeature(),
    NumberFeature()
]

# Create a scoring matrix
# Rewards:
# * identical byte values (2)
# * values that lies within the ASCII range (2 or 1)
# * numeric values close to each other (1 or 0)
# Ignores:
# * existing gaps (0)
# Discourages:
# * everything else (-1)
alphanum = map(ord, string.printable)[:62]
non_alphanum = map(ord, string.printable)[62:]
S = -1 * np.ones((257, 257))
for i in range(256):
    for j in range(256):
        diff = abs(i - j)
        if diff <= 10:
            s = 1
        elif diff <= 20:
            s = 0
        else:
            continue
        S[i,j] = s
for i in alphanum:
    for j in alphanum:
        S[i,j] = 2
for i in non_alphanum:
    for j in non_alphanum:
        S[i,j] = 1
for i in range(256):
    S[i,i] = 2
S[256,:] = np.zeros(257)
S[:,256] = np.zeros(257)
S = S.astype(np.int16)

def classify(features):
    if features[CONSTANT]:
        return CONSTANT
    if features[ASCII] > 0.8:
        return ASCII
    if features[FLAG] < 8:
        return FLAG
    if features[UNIFORM] < 0.6:
        return UNIFORM
    if features[NUMBER] < 1.2:
        return NUMBER
    else:
        return UNKNOWN

limit = 400
packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
with open('/media/data/dns-filtered/dns-30000-100-200-0.75-0.40.dump') as f:
    result = pickle.load(f)

def recluster(limit):
    from collections import defaultdict
    from sklearn.metrics import completeness_score
    msgs = [p.data[:100] for p in packets[:30000]]
    possible = {}
    for pos in range(limit):
        bins = defaultdict(list)
        for (i, msg) in enumerate(msgs):
            bins[msg[pos]].append(i)
        largest_bin = max(map(len, bins.values()))
        if 1 < len(bins) <= len(result) and largest_bin <= 0.6 * 30000:
            possible[pos] = bins
    # Do a completeness measurement on the bins with clusters as truth
    truth = np.ndarray(len(msgs), dtype=int)
    for (i, label) in enumerate(result):
        cluster = result[label]
        for j in cluster:
            truth[j] = i
    for pos in possible:
        pred = np.ndarray(len(msgs), dtype=int)
        bins = possible[pos]
        for (i, byte_key) in enumerate(bins):
            bin_ = bins[byte_key]
            for j in bin_:
                pred[j] = i
        comp = completeness_score(truth, pred)
        possible[pos] = (comp, bins)
    return possible

possible = recluster(20)
for pos in possible:
    (comp, bins) = possible[pos]
    print '##################################################################'
    print 'Predictions for pos = %d comp = %.3f' % (pos, comp)
    for byte_key in bins:
        bin_ = bins[byte_key]
        msgs = [p.data[:limit] for p in [packets[i] for i in bin_]]
        # Align the data before building the byte distributions
        # Note: We reverse the byte data so that gaps are inserted from the
        # right in order to simulate left to right parsing of variable length
        # fields
        longest = align.string_to_alignment(msgs[np.argmax(map(len, msgs))])[::-1]
        alignments = []
        for msg in msgs:
            (_, _, a) = align.align(longest,
                    align.string_to_alignment(msg)[::-1], 0, -2, S, mutual=False)
            alignments.append(a[::-1])

        distributions = np.zeros((max(map(len, alignments)), 256))
        for alignment in alignments:
            for (i, byte) in enumerate(alignment):
                if byte != 256:
                    distributions[i,byte] += 1

        predictions = []
        for (i, dist) in enumerate(distributions):
            if sum(dist) >= 0.1 * len(msgs):
                features = list(chain.from_iterable([func.get_values(dist) for
                    func in feature_functions]))
                class_ = classify(features)
            else:
                features = None
                class_ = VARIABLE
            predictions.append((features, class_))

        # Output the predictions
        print '##################################################################'
        print 'Predictions for pos = %d byte = %d size = %d' % (pos, ord(byte_key), len(bin_))
        for (features, class_) in predictions[:40]:
            print features, classes[class_]

