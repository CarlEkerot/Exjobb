#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
import align
import numpy
import itertools
import pydot

size = 100
limit = 2000
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
            score += M[i.index, j.index]
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
    def __init__(self, index):
        self.index = index

    def get_leaves(self):
        return [self]

packets = pcap_reassembler.load_pcap('../smbtorture.cap')
msgs = map(lambda x: x.data[:limit], packets[:size])

S = 3 * numpy.identity(256) - numpy.ones((256, 256))
S = S.astype(numpy.int16)

# only the upper diagonal part of this matrix is needed, build it smarter
for i in range(size):
    for j in range(i + 1, size):
        (s, _, _) = align.align(msgs[i], msgs[j], -2, S, local=True)
        M[i,j] = s

# input all the leaf nodes to this list as a start then remove and add parent nodes
# as the tree is built; when one node is left the tree is built
to_process = []
for i in range(size):
    to_process.append(LeafNode(i))

while len(to_process) > 1:
    score_max = -1
    for (A, B) in itertools.combinations(to_process, 2):
        score = A.compare_to(B)
        if score > score_max:
            to_merge = (A, B)
            score_max = score
    (A, B) = to_merge
    to_process.remove(A)
    to_process.remove(B)
    to_process.append(ParentNode(A, B, score_max))

count = 0
def build_tree(tree, node, parent):
    global count
    if type(node) is ParentNode:
        n = pydot.Node(str(count), shape='box', label=('Score: %.2f' % node.score))
    else:
        n = pydot.Node(str(count), label=str(node.index))
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

