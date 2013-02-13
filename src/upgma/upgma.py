#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import align
import numpy
import itertools
import pydot
import collections
import matplotlib.pyplot
import math

class Node(object):
    def compare_to(self, n):
        a = self.get_leaves()
        b = n.get_leaves()
        ab = list(itertools.product(a, b))
        score = 0
        for (i, j) in ab:
            min_len = min(len(i.features), len(j.features))
            score += numpy.linalg.norm(i.features[:min_len] - j.features[:min_len])
        score /= len(ab)
        return score

class ParentNode(Node):
    def __init__(self, left, right, score):
        self.left = left
        self.right = right
        self.score = score

    def get_leaves(self):
        return self.left.get_leaves() + self.right.get_leaves()

class LeafNode(Node):
    def __init__(self, index, features):
        self.index = index
        self.features = features

    def get_leaves(self):
        return [self]

def upgma(packets, size, P, entropy, limit):
    msgs = map(lambda x: x.data[:limit], packets[:size])

    to_process = []
    for (i, msg) in enumerate(msgs):
        features = []
        for (j, byte) in enumerate(msg):
            features.append(P[j,ord(byte)])
        features = numpy.asarray(features)
        to_process.append(LeafNode(i, features))

    while len(to_process) > 1:
        score_min = float('inf')
        for (A, B) in itertools.combinations(to_process, 2):
            score = A.compare_to(B)
            if score < score_min:
                to_merge = (A, B)
                score_min = score
        (A, B) = to_merge
        to_process.remove(A)
        to_process.remove(B)
        to_process.append(ParentNode(A, B, score_min))

    return to_process[0]

size = 100
limit = 100
packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)

type_dict = {}
types = []
count = 0

with open('../../cap/smb-only.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        # no = cols[0][1:]
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
            count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)

P = numpy.zeros((limit, 256))
entropy = collections.defaultdict(set)
for packet in packets[:100]:
    for (pos, val) in enumerate(packet.data[:limit]):
        entropy[pos].add(val)
        P[pos,ord(val)] += 1
P = P / len(packets)

root = upgma(packets, size, P, entropy, limit)

nodes = []
count = 0
def build_tree(tree, node, parent, max_score):
    global count
    if type(node) is ParentNode:
        n = pydot.Node(str(count), shape='box', label=('%d s: %.2f' % (count, 100 * node.score / max_score)))
    else:
        n = pydot.Node(str(count), label='%d, %d' % (packets[node.index].number, types[packets[node.index].number - 1]))
    count += 1
    nodes.append(node)
    tree.add_node(n)
    if parent:
        tree.add_edge(pydot.Edge(parent, n))
    if type(node) is ParentNode:
        build_tree(tree, node.left, n, max_score)
        build_tree(tree, node.right, n, max_score)

# output tree
tree = pydot.Dot(graph_type='graph')
build_tree(tree, root, None, root.score)
tree.write_png('tree.png')

