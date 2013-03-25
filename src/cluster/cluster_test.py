#! /usr/bin/env python

import os
import sys
import pcap_reassembler
import cluster
import pickle
import numpy as np

from itertools import product

size = 20000
limit = 200
min_samples = 50
significant_ratio = 0.75
similarity_ratio = 0.4

output_path = '/media/data/smb/'
packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.data[4:8] == '\xffSMB', packets)[:size]
truth = {}
with open('../../cap/smb-only.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        truth[int(no)] = type_[:-1]

filename = output_path + 'smb-%d-%d-%d-%.2f-%.2f' % (size, limit, min_samples,
        significant_ratio, similarity_ratio)
d = os.path.dirname(filename)
if not os.path.exists(d):
    os.makedirs(d)

args = {
    'significant_ratio': significant_ratio,
    'similarity_ratio': similarity_ratio,
}
clustering = cluster.Clustering(packets, truth, limit)
clustering.cluster(min_samples, args)
clustering.merge_clusters()

with open('%s.res' % filename, 'w') as f:
    pickle.dump(clustering.clusters, f)
with open('%s.lbl' % filename, 'w') as f:
    pickle.dump(clustering.labels, f)

metrics = clustering.get_metrics()
with open('%s.txt' % filename, 'w') as f:
    clustering.print_clustering(f)
    clustering.print_metrics(f)

