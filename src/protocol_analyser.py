from math import log, ceil
from cluster.cluster import Clustering
from state.state_inference import state_inference, render_state_diagram
from fields.field_classifier import classify_fields
from fields.field_inference import create_global_fields, create_cluster_fields, print_fields

class ProtocolAnalyser(object):
    def __init__(self, msgs, limit, truth=None):
        self.msgs   = msgs
        self.limit  = limit
        self.truth  = truth

    def cluster(self, min_samples, significant_ratio=0.75,
            similarity_ratio=0.4, max_num_types=50, header_limit=20,
            max_type_ratio=0.6):
        limited_msg_data = [msg.data[:self.limit] for msg in self.msgs]
        clustering = Clustering(limited_msg_data, self.truth)
        args = {
            'significant_ratio':    significant_ratio,
            'similarity_ratio':     similarity_ratio,
        }
        clustering.cluster(min_samples, args, max_num_types, header_limit, max_type_ratio)
        self.labels = clustering.labels
        self.clusters = clustering.clusters
        self.type_distinguishers = clustering.type_distinguishers

    def state_inference(self, filename, depth=None):
        assert self.labels is not None, ("Missing cluster labels. "
            "Clustering needs to be performed before state inference.")

        (C_M, S_M) = state_inference(self.msgs, self.labels)
        render_state_diagram(C_M, S_M, filename, depth)

    def classify_fields(self, cluster_limit=200, global_limit='min-length',
            sizes=[1, 2, 4], max_num_flag_values=10, noise_ratio=0.5, prob=0.99):
        if global_limit == 'min-length':
            global_limit = min(map(lambda m: len(m.data), self.msgs))
        num_iters = int(ceil(log(1 - prob) / log(1 - (1 - noise_ratio)**2)))

        (self.global_est, self.cluster_est) = classify_fields(self.msgs,
                self.labels, cluster_limit, global_limit, sizes,
                max_num_flag_values, noise_ratio, num_iters)
        ordered_sizes = sorted(sizes, reverse=True)
        print ' GLOBAL '.center(33, '=')
        fields = create_global_fields(self.global_est, ordered_sizes)
        print_fields(fields, global_limit)
        for label in self.cluster_est:
            print (' CLUSTER %d (%d) ' % (label, len(self.clusters[label]))).center(33, '=')
            print 'TD values:', ', '.join([str(ord(self.msgs[self.clusters[label][0]].data[i])) for i in self.type_distinguishers])
            fields = create_cluster_fields(self.cluster_est, ordered_sizes, label)
            print_fields(fields)

