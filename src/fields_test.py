#! /usr/bin/env python

import pcap_reassembler
import numpy as np
import multiprocessing as mp

from cluster import cluster
from collections import defaultdict

size = 4000
limit = 200

packets = pcap_reassembler.load_pcap('../cap/dns-30628-packets.pcap', strict=True)

clustering = cluster.Clustering(packets, {}, size, limit)
clustering.cluster(10)
clustering.merge_clusters()
clusters = clustering.result

class UnorderedTupleDict(defaultdict):
    def __getitem__(self, k):
        (k1, k2) = k
        if (k1, k2) in self.keys():
            return super(UnorderedTupleDict, self).__getitem__((k1, k2))
        else:
            return super(UnorderedTupleDict, self).__getitem__((k2, k1))

    def __setitem__(self, k, v):
        (k1, k2) = k
        if (k1, k2) in self.keys():
            return super(UnorderedTupleDict, self).__setitem__((k1, k2), v)
        else:
            return super(UnorderedTupleDict, self).__setitem__((k2, k1), v)

streams = defaultdict(list)
connections = UnorderedTupleDict(list)
for packet in packets[:size]:
    src_socket = (packet.source_addr, packet.source_port)
    dst_socket = (packet.destination_addr, packet.destination_port)
    streams[dst_socket].append(packet)
    connections[(src_socket, dst_socket)].append(packet)

label = clusters.keys()[0]
cluster = clusters[label]
consensus = clustering.consensus[label]

import align
print align.alignment_to_string(clustering.global_consensus, hex_=True)
print [packets[i].number for i in cluster]
print align.alignment_to_string(consensus, hex_=True)

from string import printable
def is_ascii(bytes_):
    ascii = map(ord, printable)
    return all((b in ascii for b in bytes_))

global_msgs = [p.data[:limit] for p in packets]
GP = np.zeros((limit, 256))
for msg in global_msgs:
    for (pos, val) in enumerate(msg):
        GP[pos,ord(val)] += 1

from scipy.stats import poisson, randint
import matplotlib.pyplot as plt
print 'GLOBAL ENTROPY'
for i in range(len(clustering.global_consensus)):
    print len(np.where(GP[i] > 0)[0])
    x = range(GP.shape[1])
    y = GP[i]
    plt.bar(x, y)
    plt.show()

cluster_msgs = [packets[i].data[:limit] for i in cluster]
CP = np.zeros((limit, 256))
for msg in cluster_msgs:
    for (pos, val) in enumerate(msg):
        CP[pos,ord(val)] += 1

print 'CLUSTER VALUES'
text_possible = len(consensus) * [False]
for i in range(len(consensus)):
    print np.where(CP[i] > 0)[0]
    if is_ascii(np.where(CP[i] > 0)[0]):
        text_possible[i] = True

print text_possible

"""
Pseudo code
-----------
# filter global consensus
for i in min_packet_length
    for v in 256
        mark (i, v) as constant where P[i][v] >= 0.999 * num_packets
for p in packets
    for (i, v) in constant
        if p[i] != v
            remove p from packets

"""

