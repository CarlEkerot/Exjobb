#! /usr/bin/env python

import pcap_reassembler
import cluster
import collections
import align
import numpy
import matplotlib.pyplot
import itertools

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)

size = 2000
clusters = cluster.cluster(packets, size, 0.2, 3)

# Get the actual types of each packet
type_dict = {}
type_strings = {}
types = []
count = 0
with open('../../cap/smb-only.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
            type_strings[count] = type_
            count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)

# Output the different types in each cluster
types_in_clusters = {}
for label in clusters:
    s = set()
    for i in clusters[label]:
        s.add(types[packets[i].number])
    types_in_clusters[label] = len(s)

# Start aligning
S = 3 * numpy.identity(257) - 1 * numpy.ones((257, 257))
S[256,:] = numpy.zeros(257)
S[:,256] = numpy.zeros(257)
S = S.astype(numpy.int16)

def merge(a1, a2):
    return [c1 if c1 == c2 else 256 for (c1, c2) in zip(a1, a2)]

cluster_consensus = []
for label in clusters:
    cluster = clusters[label]
    msgs = [packets[i].data for i in cluster]

    consensus = align.string_to_alignment(msgs[0])
    for msg in msgs[1:]:
        (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
        consensus = merge(a1, a2)

    #print 'Cluster %d - size: %d types: %d' % (label, len(cluster), types_in_clusters[label])
    #print align.alignment_to_string(consensus, hex_=True)
    #print ''

    cluster_consensus.append(consensus)

msgs = [p.data for p in packets[:size]]
min_len = min(map(len, map(lambda x: x.data, packets[:size])))
consensus = align.string_to_alignment(msgs[0])
for msg in msgs[1:]:
    (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
    consensus = merge(a1, a2)
print 'Consensus of all packets:'
consensus = consensus[:min_len]
print align.alignment_to_string(consensus, hex_=True)
print ''

left = []
height = []
indices = []
for (i, val) in enumerate(consensus):
    if val == 256:
        indices.append(i)
        s = set()
        for c in cluster_consensus:
            if c[i] != 256:
                s.add(c[i])
        num_vals = len(s)
        left.append(i)
        height.append(num_vals)

sets = collections.defaultdict(set)
for p in packets[:size]:
    for i in indices:
        sets[i].add(p.data[i])

height2 = []
for i in indices:
    height2.append(len(sets[i]))

height3 = []
important = []
for i in range(len(indices)):
    diff = 2 * height[i] - height2[i]
    height3.append(diff)
    if diff > 0:
        important.append(indices[i])

plot = matplotlib.pyplot.bar(left, height2, color='g')
plot = matplotlib.pyplot.bar(left, height, color='r')
plot = matplotlib.pyplot.bar(left, height3, color='b')
matplotlib.pyplot.show()

signatures = collections.defaultdict(list)
for label in clusters:
    signature = []
    cluster = clusters[label]
    for i in cluster:
        msg = msgs[i]
        for j in important:
            signature.append(msg[j])
    l = len(cluster)
    if l * signature[:len(important)] == signature:
        signatures[' '.join(signature[:len(important)])].append(label)

for key in signatures:
    signature = signatures[key]
    merged = []
    for label in signature:
        merged.extend(clusters[label])
    clusters[signature[0]] = merged
    for label in signature[1:]:
        del clusters[label]

for label in clusters:
    cluster = clusters[label]
    msgs = [packets[i].data for i in cluster]

    consensus = align.string_to_alignment(msgs[0])
    for msg in msgs[1:]:
        (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
        consensus = merge(a1, a2)

    print 'Cluster %d - size: %d types: %d' % (label, len(cluster), types_in_clusters[label])
    print align.alignment_to_string(consensus, hex_=True)
    print ''

print 'Total number of clusters: %d' % len(clusters)

