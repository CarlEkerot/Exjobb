#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import align
import numpy
import itertools
import pydot
import collections
import matplotlib.pyplot

size = 6
limit = 100
M = numpy.ndarray((size, size))

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

packets = pcap_reassembler.load_pcap('../cap/http.cap', strict=False)
#streams = collections.defaultdict(list)
#for packet in packets:
#    streams[(packet.source_addr, packet.destination_addr)].append(packet.data)
#for key in streams:
#    print(key)
entropy = collections.defaultdict(set)
for packet in packets:
    for (pos, val) in enumerate(packet.data[:limit]):
        entropy[pos].add(val)
#left = []
#height = []
#for pos in entropy:
#    left.append(pos)
#    height.append(len(entropy[pos]))
#plot = matplotlib.pyplot.bar(left, height, color='r')
#matplotlib.pyplot.show()

msgs = map(lambda x: x.data[:limit], packets[:size])

S = 3 * numpy.identity(256) - numpy.ones((256, 256))
S = S.astype(numpy.int16)

#for i in range(size):
#    for j in range(i + 1, size):
#        (s, _, _) = align.align(msgs[i], msgs[j], -2, S, local=True)
#        M[i,j] = s

to_process = []
for i in range(size):
    features = numpy.asarray(map(lambda (j, x): ord(x) / len(entropy[j]), enumerate(msgs[i])))
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
root = to_process[0]
build_tree(tree, root, None)

tree.write_png('tree.png')

#while True:
#    i = int(raw_input('Message index: '))
#    print('\n')
#    print(msgs[i])

