# FIXME use correct relative imports
import sys
sys.path.append('..')

import align
import scoring
import numpy as np
import sklearn.cluster
import sklearn.decomposition

from matplotlib import pyplot as plt
from collections import defaultdict
from itertools import cycle

class Clustering(object):
    def __init__(self, packets, truth, limit):
        self.packets = packets
        self.truth = truth
        self.limit = limit
        # Limit number of messages and the size of each message
        self.msgs = [p.payload[:self.limit] for p in self.packets]

    def cluster(self, min_samples, args=dict()):
        # Calculate probability matrix for the different byte values
        P = np.zeros((self.limit, 256))
        for msg in self.msgs:
            for (pos, val) in enumerate(msg):
                P[pos,ord(val)] += 1
        P = P / len(self.msgs)

        samples = []
        for (i, msg) in enumerate(self.msgs):
            features = np.zeros(self.limit)
            for (j, byte) in enumerate(msg):
                features[j] = P[j,ord(byte)]
            samples.append(features)

        # Decrease dimensionality
        X = sklearn.decomposition.PCA(0.8).fit_transform(samples)

        # Perform clustering
        opt = sklearn.cluster.OPTICS(min_samples=min_samples, ext_kwargs=args).fit(X)
        self.order = opt.ordering_
        self.reach_dists = opt.reachability_distances_
        self.labels = opt.labels_

    @property
    def clusters(self):
        clusters = defaultdict(list)
        for i, label in enumerate(self.labels):
            clusters[label].append(i)

        return clusters

    def get_metrics(self):
        # Extract samples that are not noise
        types = []
        labels = []
        for i, label in enumerate(self.labels):
            if label >= 0:
                labels.append(label)
                types.append(self.truth[self.packets[i].number])

        metrics = {
            'num': len(self.clusters),
            'homo': sklearn.metrics.homogeneity_score(types, labels),
            'comp': sklearn.metrics.completeness_score(types, labels),
            'v': sklearn.metrics.v_measure_score(types, labels),
            'ari': sklearn.metrics.adjusted_rand_score(types, labels),
            'ami': sklearn.metrics.adjusted_mutual_info_score(types, labels),
        }

        return metrics

    def print_metrics(self, f):
        metrics = self.get_metrics()

        def print_(s):
            f.write('%s\n' % s)

        print_('Total number of clusters: %d' % metrics['num'])
        print_('Homogeneity: %0.3f' % metrics['homo'])
        print_('Completeness: %0.3f' % metrics['comp'])
        print_('V-measure: %0.3f' % metrics['v'])
        print_('Adjusted Rand Index: %0.3f' % metrics['ari'])
        print_('Adjusted Mutual Information: %0.3f' % metrics['ami'])

    def plot_reachability_distances(self, filename):
        x = range(len(self.msgs))
        y = self.reach_dists[self.order]
        plt.bar(x, y, color='k')
        plt.xlabel('Samples in OPTICS order')
        plt.ylabel('Reachability distance')
        plt.savefig('%s.svg' % filename)

