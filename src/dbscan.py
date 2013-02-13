#! /usr/bin/env python

import sklearn.cluster
import pcap_reassembler
import numpy
import pydot

def compare(a, b):
    min_len = min(len(a), len(b))
    return numpy.linalg.norm(a[:min_len] - b[:min_len])

limit = 40
size = 100
packets = pcap_reassembler.load_pcap('../cap/smbtorture.cap', strict=True)

# calculate probability matrix
P = numpy.zeros((limit, 256))
for packet in packets:
    for (pos, val) in enumerate(packet.data[:limit]):
        P[pos,ord(val)] += 1
P = P / len(packets)

msgs = map(lambda x: x.data[:limit], packets[:size])
samples = []
for (i, msg) in enumerate(msgs):
    features = []
    for (j, byte) in enumerate(msg):
        features.append(P[j,ord(byte)])
    features = numpy.asarray(features)
    samples.append(features)

# Create distance matrix
nbr_samples = len(samples)
dist_matrix = numpy.zeros((nbr_samples, nbr_samples))

for i in range(nbr_samples):
    for j in range(nbr_samples):
        dist_matrix[i, j] = compare(samples[i], samples[j])

# Normalize distances
norm_dists = dist_matrix / numpy.max(dist_matrix)

# Perform clustering
db = sklearn.cluster.DBSCAN(eps=0.6, min_samples=1).fit_predict(norm_dists)

# Get actual types
type_dict = {}
types = []
count = 0
with open('../cap/smb.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
            count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)

# Display clustering
graph = pydot.Dot(graph_type='graph')
clusters = {}
for i, c in enumerate(db):
    no = packets[i].number
    node = pydot.Node(str(no), label=('%d type=%d' % (no, types[no - 1])))
    graph.add_node(node)
    if c in clusters:
        graph.add_edge(pydot.Edge(clusters[c], node))
    clusters[c] = node

graph.write_png('clusters.png')
