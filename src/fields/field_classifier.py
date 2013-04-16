# FIXME use correct relative imports
import sys
sys.path.append('..')

import align
import scoring
import numpy as np

from collections import defaultdict
from features import *
from classifiers import *

def _build_samples(data, constant=True, zero=True, flag=True, uniform=True):
    max_size = max(map(len, data))
    distributions = np.zeros((max_size, 256))
    for d in data:
        for (i, byte) in enumerate(d):
            if byte != 256:
                distributions[i,byte] += 1
    samples = []
    for dist in distributions:
        features = get_features(dist, constant, zero, flag, uniform)
        samples.append(features)
    return np.asarray(samples)

def _build_stream_and_connection_data(msgs, limit):
    stream_data = defaultdict(list)
    conn_data   = defaultdict(list)

    for msg in msgs:
        data = align.string_to_alignment(msg.data[:limit])
        stream_data[msg.stream].append(data)
        conn_data[msg.conn].append(data)

    return (stream_data, conn_data)

def _build_aligned_data(data, limit):
    limited_data = [d[:limit] for d in data]
    aligned_data = []

    longest = limited_data[np.argmax(map(len, limited_data))][::-1]
    for d in limited_data:
        (_, _, a) = align.align(longest, d[::-1], 0, -2, scoring.S,
                mutual=False)
        aligned_data.append(a[::-1])

    return aligned_data

def _field_consensus(categorized_samples, length, size, classifier):
    num_fields = int(length / size)
    fields = np.asarray(num_fields * [True])
    for samples in categorized_samples.values():
        result = classifier(samples, size)
        result += (num_fields - len(result)) * [False]
        try:
            fields = fields & result
        except:
            print type(fields), type(result), fields, result
    return fields.tolist()

def _classify_global_fields(msgs, limit, sizes, max_num_flag_values,
        noise_ratio, num_iters):
    data = [align.string_to_alignment(msg.data) for msg in msgs]
    limited_data = [d[:limit] for d in data]
    (stream_data, conn_data) = _build_stream_and_connection_data(msgs, limit)

    global_samples  = _build_samples(limited_data)
    conn_samples    = {}
    stream_samples  = {}

    for key in conn_data:
        conn_samples[key] = _build_samples(conn_data[key], zero=False,
                flag=False, uniform=False)
    for key in stream_data:
        stream_samples[key] = _build_samples(stream_data[key], zero=False,
                flag=False, uniform=False)

    global_est  = defaultdict(dict)
    conn_est    = defaultdict(dict)
    stream_est  = defaultdict(dict)

    for size in sizes:
        global_est['constants'][size]       = constant(global_samples, size)
        global_est['flags'][size]           = flag(global_samples, size, max_num_flag_values)
        global_est['uniforms'][size]        = uniform(global_samples, size)
        global_est['numbers'][size]         = number(limited_data, size)
        global_est['lengths'][size]         = length(data, size, noise_ratio, num_iters)
        conn_est['constants'][size]         = _field_consensus(conn_samples, limit, size, constant)
        stream_est['constants'][size]       = _field_consensus(stream_samples, limit, size, constant)
        stream_est['incrementals'][size]    = _field_consensus(stream_data, limit, size, incremental)

    est = {
        'global':       global_est,
        'connection':   conn_est,
        'stream':       stream_est,
    }

    return dict(est)

def _classify_cluster_fields(msgs, limit, sizes, max_num_flag_values,
        noise_ratio, num_iters, labels):
    data = [align.string_to_alignment(msg.data) for msg in msgs]

    # Create clusters from FD labels
    clusters = defaultdict(list)
    for (i, label) in enumerate(labels):
        clusters[label].append(i)

    est = defaultdict(lambda: defaultdict(dict))
    for label in clusters:
        cluster_data = [data[i] for i in clusters[label]]
        aligned_data = _build_aligned_data(cluster_data, limit)
        samples = _build_samples(aligned_data)
        for size in sizes:
            est[label]['constants'][size]       = constant(samples, size)
            est[label]['flags'][size]           = flag(samples, size, max_num_flag_values)
            est[label]['uniforms'][size]        = uniform(samples, size)
            est[label]['numbers'][size]         = number(aligned_data, size)
            est[label]['incrementals'][size]    = incremental(aligned_data, size)
            est[label]['lengths'][size]         = length(cluster_data, size,
                    noise_ratio, num_iters)

    return dict(est)

def classify_fields(msgs, labels, cluster_limit, global_limit, sizes,
        max_num_flag_values, noise_ratio, num_iters):
    global_est = _classify_global_fields(msgs, global_limit, sizes,
            max_num_flag_values, noise_ratio, num_iters)
    cluster_est = _classify_cluster_fields(msgs, cluster_limit, sizes,
            max_num_flag_values, noise_ratio, num_iters, labels)

    return (global_est, cluster_est)

