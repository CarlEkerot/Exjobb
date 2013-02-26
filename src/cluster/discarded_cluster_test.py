#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import collections
import align
import numpy
from  matplotlib import pyplot as plt
import matplotlib.font_manager
import itertools
import sklearn.cluster
import sklearn.manifold
import scipy.spatial.distance as dist
import AutomaticClustering as AutoC


def cluster(dists, eps, min_samples):
    # Perform clustering
    seed = 0
    clf = sklearn.cluster.OPTICS(min_samples=min_samples,
            metric='precomputed')
    prediction = clf.fit_predict(dists)

    result = collections.defaultdict(list)
    for i, label in enumerate(prediction):
        result[label].append(i)

    return result, clf.ordering_, clf.reachability_distances_

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
# packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)

msg_limit = 500
size = 1000

########## Get the actual types of each packet ###########

type_dict = {}
type_strings = {}
type_indices = collections.defaultdict(list)
types = []
count = 0
i = 0
with open('../../cap/smb-only.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        #if 'response' in type_:
        #    type_ = 'response'
        #else:
        #    type_ = 'request'
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
            type_strings[count] = type_
            count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)
        type_indices[type_].append(i)
        i += 1
        if i == packets[size].number - 1:
            break

###########     CREATING DISTANCE MATRIX ################

def filter_func(x):
    return 1

# Limit number of messages and the size of each message
msgs = map(lambda x: x.data[:msg_limit], packets[:size])

# Calculate probability matrix for the different byte values
P = numpy.zeros((msg_limit, 256))
for msg in msgs:
    for (pos, val) in enumerate(msg):
        P[pos,ord(val)] += 1
P = P / len(msgs)

samples = []
for (i, msg) in enumerate(msgs):
    features = numpy.zeros(msg_limit)
    for (j, byte) in enumerate(msg):
        features[j] = filter_func(j) * P[j,ord(byte)]
    samples.append(features)
samples = numpy.asarray(samples)

#################### PCA ################################

pca_samples = sklearn.decomposition.PCA(5).fit_transform(samples)

#########################################################

# Create distance matrix
dist_matrix = dist.squareform(dist.pdist(pca_samples))

# Plot samples
#mds = sklearn.manifold.MDS(dissimilarity='precomputed').fit_transform(dist_matrix)
#col = 'bgrcmykw'
#colors = itertools.cycle(col)
#markers = itertools.cycle(''.join(len(col) * m for m in 'oDsvh'))
#for t in type_dict:
#    indices = type_indices[t]
#    x = [mds[i,0] for i in indices]
#    y = [mds[i,1] for i in indices]
#    plt.scatter(x, y, s=80, c=colors.next(), marker=markers.next())
#font = matplotlib.font_manager.FontProperties()
#font.set_size('small')
#plt.legend(tuple(t for t in type_dict), loc='center left', prop=font, bbox_to_anchor=(1, 0.5))
#plt.show()

#########################################################

msgs = [p.data for p in packets[:size]]
min_len = min(map(len, map(lambda x: x.data, packets[:size])))
print 'Minimum packet length: %d' % min_len

#left = []
#height = []
#eps = 0
#for i in range(100):
clusters, O, R = cluster(dist_matrix, 0.1, 10)
RPoints = []
for o in O:
    RPoints.append(pca_samples[o])
rootNode = AutoC.automaticCluster(R, RPoints)
leaves = AutoC.getLeaves(rootNode, [])
clusters = {}
for i, leaf in enumerate(leaves):
    clusters[i] = O[leaf.start:leaf.end]

    #left.append(eps)
    #height.append(len(clusters))
    #eps += 0.01
    #print i

#plot = matplotlib.pyplot.plot(left, height)
#matplotlib.pyplot.show()

# Output samples to file
#with open('smb.dbc', 'w') as f:
#    for (i, s) in enumerate(samples):
#        t = types[packets[i].number - 1]
#        for v in s:
#            f.write('%f ' % v)
#        f.write('type%d\n' % t)

# Reachability plot
plot = matplotlib.pyplot.bar(range(len(O)), R[O], color='k')
matplotlib.pyplot.show()

# Start aligning
S = 3 * numpy.identity(257) - 1 * numpy.ones((257, 257))
S[256,:] = numpy.zeros(257)
S[:,256] = numpy.zeros(257)
S = S.astype(numpy.int16)

def merge(a1, a2):
    return [c1 if c1 == c2 else 256 for (c1, c2) in zip(a1, a2)]

cluster_consensus = []
for label in clusters:
    cluster = clusters[label]
    c_msgs = [packets[i].data[:msg_limit] for i in cluster]

    consensus = align.string_to_alignment(c_msgs[0])
    for msg in c_msgs[1:]:
        (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
        consensus = merge(a1, a2)

    cluster_consensus.append(consensus)

print 'Consensus of all packets:'
consensus = align.string_to_alignment(msgs[0][:min_len])
for msg in msgs[1:]:
    m = align.string_to_alignment(msg[:min_len])
    for i in range(min_len):
        if consensus[i] != m[i]:
            consensus[i] = 256
print align.alignment_to_string(consensus, hex_=True)
print ''

left = []
height = []
indices = []
for (i, val) in enumerate(consensus):
    if val == 256:
        indices.append(i)
        s = set()
        for c in cluster_consensus:
            if c[i] != 256:
                s.add(c[i])
        num_vals = len(s)
        left.append(i)
        height.append(num_vals)

sets = collections.defaultdict(set)
for p in packets[:size]:
    for i in indices:
        sets[i].add(p.data[i])

height2 = []
for i in indices:
    height2.append(len(sets[i]))

height3 = []
important = []
for i in range(len(indices)):
    diff = 2 * height[i] - height2[i]
    height3.append(diff)
    if diff > 0:
        important.append(indices[i])

#plot = matplotlib.pyplot.bar(left, height2, color='g')
#plot = matplotlib.pyplot.bar(left, height, color='r')
#plot = matplotlib.pyplot.bar(left, height3, color='b')
#matplotlib.pyplot.show()

signatures = collections.defaultdict(list)
for label in clusters:
    signature = []
    cluster = clusters[label]
    for i in cluster:
        msg = msgs[i]
        for j in important:
            signature.append(msg[j])
    l = len(cluster)
    if l * signature[:len(important)] == signature:
        signatures[' '.join(signature[:len(important)])].append(label)

#for key in signatures:
#    signature = signatures[key]
#    merged = []
#    for label in signature:
#        merged.extend(clusters[label])
#    clusters[signature[0]] = merged
#    for label in signature[1:]:
#        del clusters[label]

# Output the different types in each cluster
types_in_clusters = {}
for label in clusters:
    s = set()
    for i in clusters[label]:
        t = types[packets[i].number - 1]
        if t >= 0:
            s.add(type_strings[t])
        else:
            s.add('UNKNOWN')
    types_in_clusters[label] = s

for label in clusters:
    cluster = clusters[label]
    msgs = [packets[i].data[:msg_limit] for i in cluster]

    consensus = align.string_to_alignment(msgs[0])
    for msg in msgs[1:]:
        (_, a1, a2) = align.align(consensus, align.string_to_alignment(msg), -2, S)
        consensus = merge(a1, a2)

    print 'Cluster %d - size: %d' % (label, len(cluster))
    print 'Types: %d' % len(types_in_clusters[label])
    for t in types_in_clusters[label]:
        print t
    print ''
    print align.alignment_to_string(consensus, hex_=True)
    print ''

print 'Total number of clusters: %d' % len(clusters)

