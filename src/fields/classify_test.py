#! /usr/bin/env python

import pcap_reassembler
import pickle
import classifier

from fd_score import format_distinguisher_score

size = 20000
limit = 200

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.data[4:8] == '\xffSMB', packets)[:size]
msgs = [p.data[:limit] for p in packets]

######################################################3

def classify(features):
    if features[classifier.ZERO] == 1.0:
        return classifier.ZERO
    if features[classifier.CONSTANT]:
        return classifier.CONSTANT
    if features[classifier.ASCII] == 1.0:
        return classifier.ASCII
    if features[classifier.FLAG] < 8:
        return classifier.FLAG
    if features[classifier.UNIFORM] < 0.4:
        return classifier.UNIFORM
    if features[classifier.NUMBER] < 1.0:
        return classifier.NUMBER
    else:
        return classifier.UNKNOWN

import numpy as np
min_size = min(map(len, msgs))
header_msgs = [m[:min_size] for m in msgs]
distributions = np.zeros((min_size, 256))
for msg in header_msgs:
    for (i, byte) in enumerate(msg):
        distributions[i,ord(byte)] += 1
samples = []
for dist in distributions:
    features = []
    for func in classifier.feature_functions:
        features.extend(func.get_values(dist))
    samples.append(features)
samples = np.asarray(samples)

# find where the header ends
count = 0
for f in samples[::-1]:
    if classify(f) != classifier.UNKNOWN:
        break
    count += 1
header_limit = len(samples) - count

for f in samples[:header_limit]:
    print f

def number(size):
    for i in range(0, header_limit - size + 1, size):
        nums = samples[i:i+size,classifier.NUMBER]
        cons = samples[i:i+size,classifier.CONSTANT]
        classes = np.asarray(map(classify, samples[i:i+size]))
        found = np.where(np.logical_and(nums < 1.2, np.logical_not(cons)))[0].tolist()
        if not found:
            continue
        center = found[0]
        success = np.all(classes[:center] == classifier.ZERO)
        if center != size - 1:
            success = success and samples[i + center][classifier.ZERO] >= 0.1
            success = success and np.all(classes[center + 1:] == classifier.UNIFORM)
        if success:
            print i

def uniform(size):
    pass

def ascii(size):
    pass

def reserved(size):
    pass

print 'number 4'
number(4)
print 'number 2'
number(2)

######################################################3

#with open('/media/data/dns-filtered/dns-30000-100-200-0.75-0.40.dump') as f:
#    result = pickle.load(f)
#
#scores = format_distinguisher_score(packets, 20, result, max_num_types=10)
#for pos in scores:
#    score = scores[pos]
#    print 'Position: %d Score: %.3f' % (pos, score)
#
## Choose positions
#positions = [2, 3]
#
#bins = classifier.create_bins(msgs, positions)
#print '################## Positions:', positions , ' #############################'
#for key in bins:
#    bin_ = bins[key]
#    pred = classifier.classify_bin(msgs, bin_)
#    print '################## Byte values:', map(ord, key), 'Size:', len(bin_), '#############################'
#    for (feat, class_) in pred[:40]:
#        print feat, classifier.classes[class_]
#
