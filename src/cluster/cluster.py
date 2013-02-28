import align
import numpy as np
import sklearn.cluster
import sklearn.decomposition
from  matplotlib import pyplot as plt
from collections import defaultdict

class Clustering(object):
    def __init__(self, packets, truth, size, limit):
        self.packets = packets
        self.truth = truth
        self.size = size
        self.limit = limit
        # Limit number of messages and the size of each message
        self.msgs = map(lambda x: x.data[:self.limit], self.packets[:self.size])

    def cluster(self, min_samples):
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
        opt = sklearn.cluster.OPTICS(min_samples=min_samples).fit(X)
        self.order = opt.ordering_
        self.reach_dists = opt.reachability_distances_
        self.labels = opt.labels_

        self.result = defaultdict(list)
        for i, label in enumerate(self.labels):
            self.result[label].append(i)

        return self.result

    def calculate_consensus(self):
        # Create scoring matrix for alignment
        S = 3 * np.identity(257) - 1 * np.ones((257, 257))
        S[256,:] = np.zeros(257)
        S[:,256] = np.zeros(257)
        S = S.astype(np.int16)

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
        for label in self.result:
            cluster = self.result[label]
            c_msgs = [self.msgs[i] for i in cluster]

            consensus = align.string_to_alignment(c_msgs[0])
            for msg in c_msgs[1:]:
                (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
                consensus = merge(a1, a2)

            self.consensus[label] = consensus

    def merge_clusters(self):
        """
        Merges clusters with a shared consensus.
        """
        # Calculate consensus for the clusters
        self.calculate_consensus()

        consensuses = defaultdict(list)
        for label in self.consensus:
            consensus = align.alignment_to_string(self.consensus[label], hex_=True)
            consensuses[consensus].append(label)

        for c in consensuses:
            clusters = consensuses[c]
            merged = []
            for label in clusters:
                merged.extend(self.result[label])
            self.result[clusters[0]] = merged
            for label in clusters[1:]:
                del self.result[label]

    def print_clustering(self):
        if not self.result:
            return

        # Calculate consensus for the clusters
        self.calculate_consensus()

        print 'Consensus of all packets:'
        print align.alignment_to_string(self.global_consensus, hex_=True)
        print ''

        # Count the different types in each cluster
        num_types_in_clusters = defaultdict(lambda: defaultdict(int))
        for label in self.result:
            for i in self.result[label]:
                t = self.truth[self.packets[i].number]
                num_types_in_clusters[label][t] += 1

        # Print information about each cluster
        for label in self.result:
            cluster = self.result[label]
            print 'Cluster %d - size: %d types: %d' % (label,
                    len(cluster), len(num_types_in_clusters[label]))
            for t in num_types_in_clusters[label]:
                print num_types_in_clusters[label][t], t
            print ''
            print align.alignment_to_string(self.consensus[label], hex_=True)
            print ''

    def print_metrics(self):
        # Extract samples that are not noise
        types = []
        labels = []
        for i, label in enumerate(self.labels):
            if label >= 0:
                labels.append(label)
                types.append(self.truth[self.packets[i].number])

        # Print clustering statistics
        print 'Total number of clusters: %d' % len(self.result)
        print("Homogeneity: %0.3f" % sklearn.metrics.homogeneity_score(types, labels))
        print("Completeness: %0.3f" % sklearn.metrics.completeness_score(types, labels))
        print("V-measure: %0.3f" % sklearn.metrics.v_measure_score(types, labels))
        print("Adjusted Rand Index: %0.3f"
                      % sklearn.metrics.adjusted_rand_score(types, labels))
        print("Adjusted Mutual Information: %0.3f"
                      % sklearn.metrics.adjusted_mutual_info_score(types, labels))

