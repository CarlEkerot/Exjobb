# FIXME use correct relative imports
import sys
sys.path.append('..')

import numpy as np
import sklearn.cluster
import sklearn.decomposition

from collections import defaultdict

class Clustering(object):
    def __init__(self, msgs):
        self.msgs = msgs

    @property
    def clusters(self):
        clusters = defaultdict(list)
        for i, label in enumerate(self.labels):
            clusters[label].append(i)

        return clusters

    def cluster(self, min_samples, args=dict()):
        max_length = max(map(len, self.msgs))

        # Calculate probability matrix for the different byte values
        P = np.zeros((max_length, 256))
        for msg in self.msgs:
            for (pos, val) in enumerate(msg):
                P[pos,ord(val)] += 1
        P = P / len(self.msgs)

        samples = []
        for (i, msg) in enumerate(self.msgs):
            features = np.zeros(max_length)
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

    def get_metrics(self, truth):
        # Extract samples that are not noise
        types   = []
        labels  = []
        for (i, label) in enumerate(self.labels):
            if label >= 0:
                types.append(truth[i])
                labels.append(label)

        metrics = {
            'num': len(self.clusters),
            'homo': sklearn.metrics.homogeneity_score(types, labels),
            'comp': sklearn.metrics.completeness_score(types, labels),
            'v': sklearn.metrics.v_measure_score(types, labels),
            'ari': sklearn.metrics.adjusted_rand_score(types, labels),
            'ami': sklearn.metrics.adjusted_mutual_info_score(types, labels),
        }

        return metrics

