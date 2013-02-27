#! /usr/bin/env python

import pcap_reassembler
import cluster
import numpy as np

size = 5000
limit = 500
min_samples = 10

#packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)
packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)

truth = {}
with open('../../cap/smb-only.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        truth[int(no)] = type_[:-1]

clustering = cluster.Clustering(packets, truth, size, limit)
clustering.cluster(min_samples)
clustering.print_clustering()
clustering.print_metrics()

