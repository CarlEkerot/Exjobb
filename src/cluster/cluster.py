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

    def calculate_consensus(self):
        # Get clusters
        clusters = self.clusters

        # Define a function for merging alignments
        def merge(a1, a2):
            return [c1 if c1 == c2 else 256 for (c1, c2) in zip(a1, a2)]

        # Calculate global consensus
        min_len = min(map(len, self.msgs))
        self.global_consensus = align.string_to_alignment(self.msgs[0][:min_len])
        for msg in self.msgs[1:]:
            m = align.string_to_alignment(msg[:min_len])
            for i in range(min_len):
                if self.global_consensus[i] != m[i]:
                    self.global_consensus[i] = 256

        # Calculate consensus for each cluster
        self.consensus = {}
        for label in clusters:
            cluster = clusters[label]
            c_msgs = [self.msgs[i] for i in cluster]

            # TODO: This should only be calculated once.
            consensus = align.string_to_alignment(c_msgs[np.argmax(map(len, c_msgs))])[::-1]
            for msg in c_msgs:
                (_, a1, a2) = align.align(consensus,
                        align.string_to_alignment(msg)[::-1], 0, -2, scoring.S, mutual=False)
                consensus = merge(a1, a2)

            self.consensus[label] = consensus[::-1]

    def filter_clusters(self):
        """
        Filters out messages that has deviant byte values.
        """
        clusters = self.clusters

        for label in clusters:
            if label == -1:
                continue

            cluster = clusters[label]

            P = np.zeros((self.limit, 256))
            c_msgs = [self.msgs[i] for i in cluster]
            for msg in c_msgs:
                for (pos, val) in enumerate(msg):
                    P[pos,ord(val)] += 1
            P = P / len(cluster)

            delete_list = set()
            for i in cluster:
                msg = self.msgs[i]
                for (pos, byte) in enumerate(msg):
                    mostly_constant = np.where(P[pos] >= 0.95)[0]
                    if mostly_constant and ord(byte) != mostly_constant[0]:
                        delete_list.add(i)

            for index in delete_list:
                self.labels[index] = -1

    def merge_clusters(self):
        """
        Merges clusters with a shared consensus.
        """
        # Filter clusters
        self.filter_clusters()

        clusters = self.clusters

        # Calculate consensus for the clusters
        self.calculate_consensus()

        consensuses = defaultdict(list)
        for label in self.consensus:
            consensus = align.alignment_to_string(self.consensus[label], hex_=True)
            consensuses[consensus].append(label)

        for c in consensuses:
            labels = consensuses[c]
            merged = []
            for label in labels:
                merged.extend(clusters[label])
            if -1 in labels:
                merge_index = -1
            else:
                merge_index = labels[0]
            for index in merged:
                self.labels[index] = merge_index

    def print_clustering(self, f):
        if self.labels is None:
            return

        clusters = self.clusters

        # Calculate consensus for the clusters
        self.calculate_consensus()

        def print_(s):
            f.write('%s\n' % s)

        print_('Consensus of all packets:')
        print_(align.alignment_to_string(self.global_consensus, hex_=True))
        print_('')

        # Count the different types in each cluster
        num_types_in_clusters = defaultdict(lambda: defaultdict(int))
        for label in clusters:
            for i in clusters[label]:
                t = self.truth[self.packets[i].number]
                num_types_in_clusters[label][t] += 1

        # Print information about each cluster
        for label in clusters:
            cluster = clusters[label]
            print_('Cluster %d - size: %d types: %d' % (label,
                    len(cluster), len(num_types_in_clusters[label])))
            for t in num_types_in_clusters[label]:
                print_('%d %s' % (num_types_in_clusters[label][t], t))
            print_('')
            print_(align.alignment_to_string(self.consensus[label], hex_=True))
            print_('')

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

