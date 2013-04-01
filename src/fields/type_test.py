#! /usr/bin/env python

# FIXME use correct relative imports
import sys
sys.path.append('..')

import pcap_reassembler
import align
import type_estimator
import scoring
import numpy as np
import pickle

from collections import defaultdict
from features import *

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

def global_constants(samples, size):
    return type_estimator.constant(samples, size)

def global_flags(samples, size):
    return type_estimator.flag(samples, size)

def global_uniforms(samples, size):
    return type_estimator.uniform(samples, size)

def global_numbers(samples, size):
    return type_estimator.number(samples, size)

def global_lengths(msgs, size):
    return type_estimator.length(msgs, size)

def connection_constants(msgs, connection_msgs, connection_mapping, size):
    fields = np.asarray(int(len(msgs[0]) / size) * [True])
    for connection_id in connection_mapping.values():
        conn_indices = connection_msgs[connection_id]
        conn_msgs = [msgs[i] for i in conn_indices]
        samples = build_samples(conn_msgs, zero=False, flag=False,
                uniform=False, number=False)
        fields = fields & type_estimator.constant(samples, size)
    return fields.tolist()

def stream_constants(msgs, stream_msgs, size):
    fields = np.asarray(int(len(msgs[0]) / size) * [True])
    for msg_indices in stream_msgs.values():
        strm_msgs = [msgs[i] for i in msg_indices]
        samples = build_samples(strm_msgs, zero=False, flag=False,
                uniform=False, number=False)
        fields = fields & type_estimator.constant(samples, size)
    return fields.tolist()

def stream_incrementals(msgs, stream_msgs, size):
    fields = np.asarray(int(len(msgs[0]) / size) * [True])
    for msg_indices in stream_msgs.values():
        strm_msgs = [msgs[i] for i in msg_indices]
        fields = fields & type_estimator.incremental(strm_msgs, size)
    return fields.tolist()

def cluster_incrementals(msgs, size):
    return type_estimator.incremental(msgs, size)

cluster_lengths     = global_lengths
cluster_constants   = global_constants
cluster_flags       = global_flags
cluster_uniforms    = global_uniforms
cluster_numbers     = global_numbers

size = 20000

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.payload[4:8] == '\xffSMB', packets)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/tftp.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap',
#         layer=pcap_reassembler.NETWORK_LAYER)
msgs = [align.string_to_alignment(p.payload) for p in packets]
# This should be able to be overridden from user input.
limit = min(map(len, msgs))
limited_msgs = [m[:limit] for m in msgs]

filename = '/media/data/smb/smb-20000-200-50-0.75-0.40'
with open(filename + '.fdl') as f:
    labels = pickle.load(f)

# Gather message indices from each individual stream and connection
connection_mapping = {}
next_connection_id = 0
stream_msgs  = defaultdict(list)
connection_msgs = defaultdict(list)
for (i, p) in enumerate(packets):
    src_socket = (p.src_addr, p.src_port)
    dst_socket = (p.dst_addr, p.dst_port)
    sockets    = (src_socket, dst_socket)
    if sockets not in connection_mapping:
        connection_mapping[sockets] = next_connection_id
        connection_mapping[sockets[::-1]] = next_connection_id
        next_connection_id += 1

    connection_id = connection_mapping[sockets]
    stream_msgs[sockets].append(i)
    connection_msgs[connection_id].append(i)

# Create clusters from FD labels
clusters = defaultdict(list)
for (i, label) in enumerate(labels):
    clusters[label].append(i)

estimations = defaultdict(dict)
global_samples = build_samples(limited_msgs)

for size in [1, 2, 4]:
    estimations['global_lengths'][size] = global_lengths(msgs[:100], size)
    estimations['global_constants'][size] = global_constants(global_samples, size)
    estimations['global_flags'][size] = global_flags(global_samples, size)
    estimations['global_uniforms'][size] = global_uniforms(global_samples, size)
    estimations['global_numbers'][size] = global_numbers(global_samples, size)
    estimations['connection_constants'][size] = connection_constants(limited_msgs,
            connection_msgs, connection_mapping, size)
    estimations['stream_constants'][size] = stream_constants(limited_msgs, stream_msgs, size)
    estimations['stream_incrementals'][size] = stream_incrementals(limited_msgs, stream_msgs, size)

limit = 200

cluster_estimations = defaultdict(lambda: defaultdict(dict))
for label in clusters:
    cluster_msgs = [msgs[i] for i in clusters[label]]
    lim_cluster_msgs = [msg[:limit] for msg in cluster_msgs]
    longest = lim_cluster_msgs[np.argmax(map(len, lim_cluster_msgs))][::-1]
    (_, _, a) = align.align(longest, longest, 0, -2, scoring.S, mutual=False)
    aligned_msgs = []
    for msg in lim_cluster_msgs:
        (_, _, a) = align.align(longest, msg[::-1], 0, -2, scoring.S, mutual=False)
        aligned_msgs.append(a[::-1])
    samples = build_samples(aligned_msgs)
    for size in [1, 2, 4]:
        cluster_estimations[label]['lengths'][size] = cluster_lengths(cluster_msgs[:100], size)
        cluster_estimations[label]['incrementals'][size] = cluster_incrementals(aligned_msgs, size)
        cluster_estimations[label]['constants'][size] = cluster_constants(samples, size)
        cluster_estimations[label]['flags'][size] = cluster_flags(samples, size)
        cluster_estimations[label]['uniforms'][size] = cluster_uniforms(samples, size)
        cluster_estimations[label]['numbers'][size] = cluster_numbers(samples, size)

with open('%s.est' % filename, 'w') as f:
    pickle.dump(dict(estimations), f)
with open('%s.cest' % filename, 'w') as f:
    pickle.dump(dict(cluster_estimations), f)

