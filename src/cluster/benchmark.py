#! /usr/bin/env python

import os
import sys
import pcap_reassembler
import cluster
import numpy as np
import multiprocessing as mp

from itertools import product

#sizes = [100, 500, 1000, 3000, 5000, 10000, 15000, 20000, 30000]
#limits = [20, 40, 60, 100, 500]
#min_samples = [1, 3, 5, 10, 20, 50]
#significant_ratios = [0.4, 0.6, 0.70, 0.75, 0.80, 0.85, 0.90]
#similarity_ratios = [0.4, 0.5, 0.6, 0.7, 0.8]
sizes = [100, 500]
limits = [20, 40]
min_samples = [1, 3]
significant_ratios = [0.4, 0.6]
similarity_ratios = [0.4, 0.5]

packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
truth = {}
with open('../../cap/dns.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        truth[int(no)] = type_[:-1]

met_q = mp.Queue()

def benchmark(size, limit, min_samples, significant_ratio, similarity_ratio):
    filename = 'dns/dns-%d-%d-%d-%.2f-%.2f' % (size, limit, min_samples,
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
    with open('%s.txt' % filename, 'w') as f:
        clustering.print_clustering(f)
        clustering.print_metrics(f)
    clustering.plot_reachability_distances(filename)

    metrics = clustering.get_metrics()
    row = [
            size,
            limit,
            min_samples,
            significant_ratio,
            similarity_ratio,
            metrics['num'],
            metrics['homo'],
            metrics['comp'],
            metrics['v'],
            metrics['ari'],
            metrics['ami'],
    ]
    met_q.put(row)

args = list(product(sizes, limits, min_samples, significant_ratios, similarity_ratios))
pool = mp.Pool()
for arg in args:
    pool.apply_async(benchmark, arg)
pool.close()
pool.join()

with open('dns-metrics-summary.csv', 'w') as f:
    f.write('size,limit,min_samples,significant_ratio,similarity_ratio,num,homo,comp,v,ari,ami\n')
    while not met_q.empty():
        row = met_q.get()
        f.write('%s\n' % ','.join(map(str,row)))

