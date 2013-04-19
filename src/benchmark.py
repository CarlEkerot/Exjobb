#! /usr/bin/env python

import os
import sys
import multiprocessing as mp

from itertools import product
from pickle import dump
from pcap_glue import build_messages
from protocol_analyser import ProtocolAnalyser

# Suppress stdout
#sys.stdout = open(os.devnull, 'w')

sizes = [1000]
min_samples = [10]

input_file = '/media/data/cap/dns-30628-packets.pcap'
output_path = '/media/data/dns/'

msgs = build_messages(input_file)

def benchmark(size, min_samples):
    an = ProtocolAnalyser(msgs[:size], 200)
    an.cluster(min_samples, max_num_types=10)
    an.classify_fields()

    data = {
        'size':         size,
        'min_samples':  min_samples,
        'labels':       an.labels,
        'global_est':   an.global_est,
        'cluster_est':  an.cluster_est,
    }

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    filename = output_path + '%d-%d.pickle' % (size, min_samples)
    with open(filename, 'w') as f:
        dump(data, f)

args = list(product(sizes, min_samples))
pool = mp.Pool()
for arg in args:
    pool.apply_async(benchmark, arg)
pool.close()
pool.join()

