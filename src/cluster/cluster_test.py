#! /usr/bin/env python

import os
import sys
import pcap_reassembler
import cluster
import pickle
import numpy as np

from itertools import product

# check if filtered fixes cluster 1 in 15000-100-200-0.60-0.40

output_path = '/media/data/dns-filtered/'
packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
truth = {}
with open('../../cap/dns.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        truth[int(no)] = type_[:-1]

def benchmark(size, limit, min_samples, significant_ratio, similarity_ratio):
    filename = output_path + 'dns-%d-%d-%d-%.2f-%.2f' % (size, limit, min_samples,
            significant_ratio, similarity_ratio)
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        os.makedirs(d)

    args = {
        'significant_ratio': significant_ratio,
        'similarity_ratio': similarity_ratio,
    }
    clustering = cluster.Clustering(packets, truth, size, limit)
    clustering.cluster(min_samples, args)
    clustering.merge_clusters()

    with open('%s.dump' % filename, 'w') as f:
        pickle.dump(clustering.result, f)

    metrics = clustering.get_metrics()
    with open('%s.txt' % filename, 'w') as f:
        clustering.print_clustering(f)
        clustering.print_metrics(f)

benchmark(30000, 100, 200, 0.75, 0.4)

