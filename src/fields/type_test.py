#! /usr/bin/env python

# FIXME use correct relative imports
import sys
sys.path.append('..')

import pcap_reassembler
import align
import scoring
import numpy as np
import pickle

from collections import defaultdict
from features import *
from classifiers import *

def build_samples(msgs, constant=True, zero=True, flag=True, uniform=True, number=True):
    max_size = max(map(len, msgs))
    distributions = np.zeros((max_size, 256))
    for msg in msgs:
        for (i, byte) in enumerate(msg):
            if byte != 256:
                distributions[i,byte] += 1
    samples = []
    for dist in distributions:
        features = get_features(dist, constant, zero, flag, uniform, number)
        samples.append(features)
    return np.asarray(samples)

def build_stream_and_connection_msgs(packets, limit):
    connection_mapping = {}
    stream_msgs     = defaultdict(list)
    connection_msgs = defaultdict(list)
    next_connection_id = 0

    for (i, p) in enumerate(packets):
        src_socket = (p.src_addr, p.src_port)
        dst_socket = (p.dst_addr, p.dst_port)
        sockets    = (src_socket, dst_socket)
        if sockets not in connection_mapping:
            connection_mapping[sockets] = next_connection_id
            connection_mapping[sockets[::-1]] = next_connection_id
            next_connection_id += 1
        connection_id = connection_mapping[sockets]
        msg = align.string_to_alignment(packets[i].payload[:limit])
        stream_msgs[sockets].append(msg)
        connection_msgs[connection_id].append(msg)

    return (stream_msgs, connection_msgs)

def build_aligned_msgs(msgs, limit):
    msgs = [msg[:limit] for msg in msgs]
    aligned_msgs = []

    longest = msgs[np.argmax(map(len, msgs))][::-1]
    for msg in msgs:
        (_, _, a) = align.align(longest, msg[::-1], 0, -2, scoring.S,
                mutual=False)
        aligned_msgs.append(a[::-1])

    return aligned_msgs

def field_consensus(categorized_samples, length, size, classifier):
    fields = np.asarray(int(length / size) * [True])
    for samples in categorized_samples.values():
        fields = fields & classifier(samples, size)
    return fields.tolist()

size = 20000

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.payload[4:8] == '\xffSMB', packets)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/tftp.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap',
#         layer=pcap_reassembler.NETWORK_LAYER)

filename = '/media/data/smb/smb-20000-200-50-0.75-0.40'
with open(filename + '.fdl') as f:
    labels = pickle.load(f)

# Create clusters from FD labels
clusters = defaultdict(list)
for (i, label) in enumerate(labels):
    clusters[label].append(i)

msgs = [align.string_to_alignment(p.payload) for p in packets]
# This should be able to be overridden from user input.
limit = min(map(len, msgs))
cluster_limit = 200
limited_msgs = [m[:limit] for m in msgs]
(stream_msgs, connection_msgs) = build_stream_and_connection_msgs(packets, limit)

global_samples = build_samples(limited_msgs)
connection_samples = {}
stream_samples = {}
for key in connection_msgs:
    connection_samples[key] = build_samples(connection_msgs[key], zero=False,
            flag=False, uniform=False, number=False)
for key in stream_msgs:
    stream_samples[key] = build_samples(stream_msgs[key], zero=False,
            flag=False, uniform=False, number=False)

estimations = defaultdict(dict)
cluster_estimations = defaultdict(lambda: defaultdict(dict))

for size in [1, 2, 4]:
    estimations['global_lengths'][size]         = length(msgs[:100], size)
    estimations['global_constants'][size]       = constant(global_samples, size)
    estimations['global_flags'][size]           = flag(global_samples, size)
    estimations['global_uniforms'][size]        = uniform(global_samples, size)
    estimations['global_numbers'][size]         = number(global_samples, size)
    estimations['connection_constants'][size]   = field_consensus(connection_samples, limit, size, constant)
    estimations['stream_constants'][size]       = field_consensus(stream_samples, limit, size, constant)
    estimations['stream_incrementals'][size]    = field_consensus(stream_msgs, limit, size, incremental)

for label in clusters:
    cluster_msgs = [msgs[i] for i in clusters[label]]
    aligned_msgs = build_aligned_msgs(cluster_msgs, cluster_limit)
    samples = build_samples(aligned_msgs)
    for size in [1, 2, 4]:
        cluster_estimations[label]['lengths'][size]         = length(cluster_msgs[:100], size)
        cluster_estimations[label]['incrementals'][size]    = incremental(aligned_msgs, size)
        cluster_estimations[label]['constants'][size]       = constant(samples, size)
        cluster_estimations[label]['flags'][size]           = flag(samples, size)
        cluster_estimations[label]['uniforms'][size]        = uniform(samples, size)
        cluster_estimations[label]['numbers'][size]         = number(samples, size)

with open('%s.est' % filename, 'w') as f:
    pickle.dump(dict(estimations), f)
with open('%s.cest' % filename, 'w') as f:
    pickle.dump(dict(cluster_estimations), f)

