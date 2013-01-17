#! /usr/bin/env python

import sys

samples = []

def annotate(msg, protocol):
    classifier = classify(msg, protocol)
    for pos in range(len(msg)):
        features = extract_features(msg, pos)
        target = classifier.next()
        samples.append((target, features))

def extract_features(msg, pos):
    if pos > 0:
        pred = msg[pos-1]
    else:
        pred = None
    if pos < len(msg) - 1:
        succ = msg[pos+1]
    else:
        succ = None
    features = (pos, msg[pos], pred, succ)
    return features

def classify(msg, protocol):
    boundary = 0
    offsets = []
    for field in protocol:
        if field.isdigit():
            boundary += int(field)
            offsets.append(boundary)
        elif field[0] == '@':
            idx = int(field[1:])
            bytes_ = msg[offsets[idx-1]:offsets[idx]]
            boundary += int(bytes_.encode('hex'), 16) - 8
            offsets.append(boundary)
        else:
            raise ValueError
    i = 0
    for pos in range(len(msg)):
        target = 0
        if pos == offsets[i] - 1:
            target = 1
            i += 1
        yield target

protocol_filename   = sys.argv[1]
data_filename       = sys.argv[2]

with open(protocol_filename) as f:
    protocol = f.read().split()

with open(data_filename) as f:
    for msg in f:
        annotate(msg[:-1].decode('hex'), protocol)

for sample in samples:
    (target, features) = sample
    s = '%d 1:%d ' % (target, features[0])
    for (i, feature) in enumerate(features[1:]):
        if feature:
            f = int(feature.encode('hex'), 16)
        else:
            f = 257
        s += '%d:%d ' % (i, f)
    print(s)

