#! /usr/bin/env python

import os
import sys
import pcap_reassembler
import cluster
import pickle
import numpy as np

from itertools import product
from fd_clustering import format_distinguisher_clustering

size = 20000
limit = 200
min_samples = 50
significant_ratio = 0.75
similarity_ratio = 0.4

output_path = '/media/data/smb/'
packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.payload[4:8] == '\xffSMB', packets)[:size]
msgs = [p.payload[:limit] for p in packets]
nums = [p.number for p in packets]
truth = []
with open('../../cap/smb-only.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        if int(no) in nums:
            truth.append(type_[:-1])

filename = output_path + 'smb-%d-%d-%d-%.2f-%.2f' % (size, limit, min_samples,
        significant_ratio, similarity_ratio)
d = os.path.dirname(filename)
if not os.path.exists(d):
    os.makedirs(d)

args = {
    'significant_ratio': significant_ratio,
    'similarity_ratio': similarity_ratio,
}
clustering = cluster.Clustering(msgs)
clustering.cluster(min_samples, args)

fd_labels = format_distinguisher_clustering(msgs, clustering.labels,
        max_num_types=100)

with open('%s.res' % filename, 'w') as f:
    pickle.dump(clustering.clusters, f)
with open('%s.lbl' % filename, 'w') as f:
    pickle.dump(clustering.labels, f)
with open('%s.fdl' % filename, 'w') as f:
    pickle.dump(fd_labels, f)

metrics = clustering.get_metrics(truth)
with open('%s.txt' % filename, 'w') as f:
    def print_(s):
        f.write('%s\n' % s)

    print_('Total number of clusters: %d' % metrics['num'])
    print_('Homogeneity: %0.3f' % metrics['homo'])
    print_('Completeness: %0.3f' % metrics['comp'])
    print_('V-measure: %0.3f' % metrics['v'])
    print_('Adjusted Rand Index: %0.3f' % metrics['ari'])
    print_('Adjusted Mutual Information: %0.3f' % metrics['ami'])

