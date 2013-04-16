import numpy as np
import sklearn.cluster
import sklearn.decomposition

from collections import defaultdict
from sklearn.metrics import completeness_score

class Clustering(object):
    def __init__(self, msgs, truth=None):
        self.msgs = msgs
        self.truth = truth

    @property
    def clusters(self):
        clusters = defaultdict(list)
        for i, label in enumerate(self.labels):
            clusters[label].append(i)

        return clusters

    def cluster(self, min_samples, optics_args, max_num_types, header_limit,
            max_type_ratio):
        self.labels = self._optics_clustering(min_samples, optics_args)
        scores = self._format_distinguisher_score(max_num_types, header_limit,
                max_type_ratio)
        self.labels = self._format_distinguisher_clustering(scores, max_num_types)

    def _optics_clustering(self, min_samples, args):
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
        #self.order = opt.ordering_
        #self.reach_dists = opt.reachability_distances_
        return opt.labels_

    def _format_distinguisher_score(self, max_num_types=50, header_limit=20,
            max_type_ratio=0.6):
        min_length = min(map(len, self.msgs))
        header_limit = min(header_limit, min_length)
        possible = {}
        scores = []

        for pos in range(header_limit):
            bins = defaultdict(list)
            for (i, msg) in enumerate(self.msgs):
                bins[msg[pos]].append(i)
            largest_bin = max(map(len, bins.values()))
            max_bin_size = max_type_ratio * len(self.msgs)
            if 1 < len(bins) <= max_num_types and largest_bin <= max_bin_size:
                possible[pos] = bins

        # Calculate completeness on the bins with labels as truth
        for pos in possible:
            pred = np.ndarray(len(self.msgs), dtype=int)
            bins = possible[pos]
            for (i, byte) in enumerate(bins):
                bin_ = bins[byte]
                for j in bin_:
                    pred[j] = i
            # Remove messages in noise cluster
            labels_no_noise = []
            pred = pred.tolist()
            new_pos = 0
            for label in self.labels:
                if label != -1:
                    labels_no_noise.append(label)
                    new_pos += 1
                else:
                    del pred[new_pos]
            comp = completeness_score(labels_no_noise, pred)
            scores.append((comp, pos))

        return scores

    def _format_distinguisher_clustering(self, scores, max_num_types):
        scores.sort(reverse=True)

        positions = []
        for (_, pos) in scores:
            types = set()
            for msg in self.msgs:
                types.add(tuple(msg[i] for i in positions + [pos]))
            if len(types) >= max_num_types:
                break
            positions.append(pos)

        if not positions:
            print 'Could not find any format distinguishers.'
            return self.labels
        print 'Chosen format distinguishers: ' + ', '.join(map(str, positions))

        bins = defaultdict(list)
        for (i, msg) in enumerate(self.msgs):
            key = ''.join([msg[p] for p in positions])
            bins[key].append(i)

        fd_labels = np.ndarray(len(self.labels))
        for (i, key) in enumerate(bins):
            bin_ = bins[key]
            for index in bin_:
                fd_labels[index] = i

        return fd_labels

    def get_metrics(self):
        if self.truth is None:
            return None

        # Extract samples that are not noise
        types   = []
        labels  = []
        for (i, label) in enumerate(self.labels):
            if label >= 0:
                types.append(self.truth[i])
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

