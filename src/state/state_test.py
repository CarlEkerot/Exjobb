#! /usr/bin/env python

# FIXME use correct relative imports
import sys
sys.path.append('../cluster')

import state_inference
import pickle
import pcap_reassembler

from collections import defaultdict
from fd_clustering import format_distinguisher_clustering

size = 20000
limit = 200

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.data[4:8] == '\xffSMB', packets)[:size]
msgs = [p.data[:limit] for p in packets]

with open('/media/data/smb/smb-20000-200-50-0.75-0.40.lbl') as f:
    labels = pickle.load(f)
labels = format_distinguisher_clustering(msgs, labels, max_num_types=220, max_type_ratio=0.7)

(C_M, S_M) = state_inference.state_inference(packets, labels)
state_inference.render_state_diagram(C_M, S_M, 'state_diagram.png', 5)

print 'States:'
truth = {}
with open('../../cap/smb-only.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        truth[int(no)] = type_[:-1]
clusters = defaultdict(list)
for i, label in enumerate(labels):
    clusters[label].append(i)
for label in clusters:
    cluster = clusters[label]
    print label, truth[packets[cluster[0]].number], packets[cluster[0]].number

