import numpy as np

from collections import defaultdict
from sklearn.metrics import completeness_score

def format_distinguisher_score(msgs, labels, max_num_types, header_limit,
        max_type_ratio):
    shortest_msg = min(map(len, msgs))
    header_limit = min(header_limit, shortest_msg)
    possible = {}
    scores = []

    for pos in range(header_limit):
        bins = defaultdict(list)
        for (i, msg) in enumerate(msgs):
            bins[msg[pos]].append(i)
        largest_bin = max(map(len, bins.values()))
        max_bin_size = max_type_ratio * len(msgs)
        if 1 < len(bins) <= max_num_types and largest_bin <= max_bin_size:
            possible[pos] = bins

    # Calculate completeness on the bins with labels as truth
    for pos in possible:
        pred = np.ndarray(len(msgs), dtype=int)
        bins = possible[pos]
        for (i, byte) in enumerate(bins):
            bin_ = bins[byte]
            for j in bin_:
                pred[j] = i
        comp = completeness_score(labels, pred)
        scores.append((comp, pos, len(bins)))

    return scores

def format_distinguisher_clustering(msgs, labels, max_num_types=50,
        header_limit=20, max_type_ratio=0.6):
    scores = format_distinguisher_score(msgs, labels, max_num_types,
            header_limit, max_type_ratio)
    scores.sort(reverse=True)

    positions = []
    num_types = 1
    for (_, pos, pos_types) in scores:
        num_types *= pos_types
        if num_types >= max_num_types:
            break
        positions.append(pos)

    bins = defaultdict(list)
    for (i, msg) in enumerate(msgs):
        key = ''.join([msg[p] for p in positions])
        bins[key].append(i)

    fd_labels = np.ndarray(len(labels))
    for (i, key) in enumerate(bins):
        bin_ = bins[key]
        for index in bin_:
            fd_labels[index] = i

    return fd_labels

