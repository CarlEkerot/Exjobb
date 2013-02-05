#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import align
import numpy
import itertools
import pydot
import collections
import matplotlib.pyplot

class Node(object):
    def compare_to(self, n):
        a = self.get_leaves()
        b = n.get_leaves()
        ab = list(itertools.product(a, b))
        score = 0
        for (i, j) in ab:
            if i > j:
                (i, j) = (j, i)
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

def upgma(packets, size, limit=100):
    entropy = collections.defaultdict(set)
    for packet in packets:
        for (pos, val) in enumerate(packet.data[:limit]):
            entropy[pos].add(val)

    msgs = map(lambda x: x.data[:limit], packets[:size])

    to_process = []
    for (i, msg) in enumerate(msgs):
        features = numpy.asarray(map(lambda (j, x): ord(x) / len(entropy[j]), enumerate(msg)))
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
packets = pcap_reassembler.load_pcap('../cap/dns-30628-packets.pcap', strict=True)
root = upgma(packets, size)

count = 0
def build_tree(tree, node, parent):
    global count
    if type(node) is ParentNode:
        n = pydot.Node(str(count), shape='box', label=('Score: %.2f' % node.score))
    else:
        n = pydot.Node(str(count), label=packets[node.index].number)
    count += 1
    tree.add_node(n)
    if parent:
        tree.add_edge(pydot.Edge(parent, n))
    if type(node) is ParentNode:
        build_tree(tree, node.left, n)
        build_tree(tree, node.right, n)

# output tree
tree = pydot.Dot(graph_type='graph')
build_tree(tree, root, None)
tree.write_png('tree.png')

