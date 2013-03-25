import align
import scoring
import numpy as np

from features import *
from collections import defaultdict

CONSTANT    = 0
FLAG        = 1
ZERO        = 2
ASCII       = 3
UNIFORM     = 4
NUMBER      = 5
UNKNOWN     = 6
VARIABLE    = 7

classes = [
    'CONSTANT',
    'FLAG',
    'ZERO',
    'ASCII',
    'UNIFORM',
    'NUMBER',
    'UNKNOWN',
    'VARIABLE',
]

feature_functions = [
    ConstantFeature(),
    FlagFeature(),
    ZeroFeature(),
    AsciiFeature(),
    UniformFeature(),
    NumberFeature()
]

def classify(features):
    if features[ZERO] == 1.0:
        return ZERO
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

def classify_bin(msgs, bin_, significant_limit=0.1):
    bin_msgs = [msgs[i] for i in bin_]
    # Align the data before building the byte distributions
    # Note: We reverse the byte data so that gaps are inserted from the
    # right in order to simulate left to right parsing of variable length
    # fields
    longest = align.string_to_alignment(bin_msgs[np.argmax(map(len, bin_msgs))])[::-1]
    alignments = []
    for msg in bin_msgs:
        (_, _, a) = align.align(longest,
                align.string_to_alignment(msg)[::-1], 0, -2, scoring.S, mutual=False)
        alignments.append(a[::-1])

    distributions = np.zeros((max(map(len, alignments)), 256))
    for alignment in alignments:
        for (i, byte) in enumerate(alignment):
            if byte != 256:
                distributions[i,byte] += 1

    predictions = []
    for (i, dist) in enumerate(distributions):
        if sum(dist) >= significant_limit * len(bin_msgs):
            features = []
            for func in feature_functions:
                features.extend(func.get_values(dist))
            class_ = classify(features)
        else:
            features = None
            class_ = VARIABLE
        predictions.append((features, class_))

    return predictions

