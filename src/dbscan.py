#! /usr/bin/env python

import sklearn.cluster
import scipy.spatial.distance as dist
import pcap_reassembler
import numpy
import collections

limit = 60
size = 1000
packets = pcap_reassembler.load_pcap('../cap/smb_pure.cap', strict=True)

type_dict = {}
types = []
count = 0
real_type = []
with open('../cap/smb_pure.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        real_type.append(cols[-1])
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
        count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)

# calculate probability matrix
P = numpy.zeros((limit, 256))
for packet in packets:
    for (pos, val) in enumerate(packet.data[:limit]):
        P[pos,ord(val)] += 1
P = P / len(packets)

msgs = map(lambda x: x.data[:limit], packets[:size])
samples = []
for (i, msg) in enumerate(msgs):
    features = numpy.zeros(limit)
    for (j, byte) in enumerate(msg):
        features[j] = (P[j,ord(byte)])
    samples.append(features)

# Create distance matrix
dist_matrix = dist.squareform(dist.pdist(samples))

# Normalize distances
norm_dists = dist_matrix / numpy.max(dist_matrix)

# Perform clustering
db = sklearn.cluster.DBSCAN(eps=0.55, min_samples=3).fit_predict(norm_dists)

result_dict = collections.defaultdict(list)
for i, result in enumerate(db):
    result_dict[result].append(i)

print result_dict

for label in result_dict:
    print str(label) + ": "
    for real in result_dict[label][:30]:
        print packets[real].number, types[real], real_type[real][:-2]
    print ""
