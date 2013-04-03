# FIXME use correct relative imports
import sys
sys.path.append('..')

import align
import scoring
import numpy as np

from collections import defaultdict
from features import *
from classifiers import *

def build_samples(msgs, constant=True, zero=True, flag=True, uniform=True,
        number=True):
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
    num_fields = int(length / size)
    fields = np.asarray(num_fields * [True])
    for samples in categorized_samples.values():
        result = classifier(samples, size)
        result += (num_fields - len(result)) * [False]
        fields = fields & result
    return fields.tolist()

def classify_fields(packets, labels, cluster_limit, global_limit='min-length',
        sizes=[1, 2, 4]):
    msgs = [align.string_to_alignment(p.payload) for p in packets]

    if global_limit == 'min-length':
        global_limit = min(map(len, msgs))

    global_est = classify_global_fields(msgs, packets, global_limit, sizes)
    cluster_est = classify_cluster_fields(msgs, labels, cluster_limit, sizes)

    return (global_est, cluster_est)

def classify_global_fields(msgs, packets, limit, sizes):
    limited_msgs = [m[:limit] for m in msgs]
    (stream_msgs, conn_msgs) = build_stream_and_connection_msgs(packets, limit)

    global_samples  = build_samples(limited_msgs)
    conn_samples    = {}
    stream_samples  = {}

    for key in conn_msgs:
        conn_samples[key] = build_samples(conn_msgs[key], zero=False,
                flag=False, uniform=False, number=False)
    for key in stream_msgs:
        stream_samples[key] = build_samples(stream_msgs[key], zero=False,
                flag=False, uniform=False, number=False)

    global_est  = defaultdict(dict)
    conn_est    = defaultdict(dict)
    stream_est  = defaultdict(dict)

    for size in sizes:
        global_est['constants'][size]       = constant(global_samples, size)
        global_est['flags'][size]           = flag(global_samples, size)
        global_est['uniforms'][size]        = uniform(global_samples, size)
        global_est['numbers'][size]         = number(global_samples, size)
        global_est['lengths'][size]         = length(msgs[:100], size)
        conn_est['constants'][size]         = field_consensus(conn_samples, limit, size, constant)
        stream_est['constants'][size]       = field_consensus(stream_samples, limit, size, constant)
        stream_est['incrementals'][size]    = field_consensus(stream_msgs, limit, size, incremental)

    est = {
        'global':       global_est,
        'connection':   conn_est,
        'stream':       stream_est,
    }

    return dict(est)

def classify_cluster_fields(msgs, labels, limit, sizes):
    # Create clusters from FD labels
    clusters = defaultdict(list)
    for (i, label) in enumerate(labels):
        clusters[label].append(i)

    est = defaultdict(lambda: defaultdict(dict))
    for label in clusters:
        cluster_msgs = [msgs[i] for i in clusters[label]]
        aligned_msgs = build_aligned_msgs(cluster_msgs, limit)
        samples = build_samples(aligned_msgs)
        for size in sizes:
            est[label]['constants'][size]       = constant(samples, size)
            est[label]['flags'][size]           = flag(samples, size)
            est[label]['uniforms'][size]        = uniform(samples, size)
            est[label]['numbers'][size]         = number(samples, size)
            est[label]['incrementals'][size]    = incremental(aligned_msgs, size)
            est[label]['lengths'][size]         = length(cluster_msgs[:100], size)

    return dict(est)

