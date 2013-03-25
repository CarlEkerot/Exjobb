from __future__ import division

import numpy as np

from collections import defaultdict
from pydot import Dot, Node, Edge

def state_inference(packets, labels):
    num_labels = max(labels) + 1
    C_M = np.zeros((num_labels + 1, num_labels + 1), dtype=int)
    S_M = np.zeros((num_labels + 1, num_labels + 1), dtype=int)
    connection_states = defaultdict(lambda: num_labels)
    connection_clients = {}
    connection_mapping = {}
    next_connection_id = 0

    for (i, p) in enumerate(packets):
        src_socket = (p.src_addr, p.src_port)
        dst_socket = (p.dst_addr, p.dst_port)
        sockets = (src_socket, dst_socket)
        if sockets not in connection_mapping:
            connection_mapping[sockets] = next_connection_id
            connection_mapping[sockets[::-1]] = next_connection_id
            connection_clients[next_connection_id] = p.src_addr
            next_connection_id += 1

        connection_id = connection_mapping[sockets]
        client = connection_clients[connection_id]
        curr_state = connection_states[connection_id]
        next_state = labels[i]
        if p.src_addr == client:
            C_M[curr_state,next_state] += 1
        else:
            S_M[curr_state,next_state] += 1
        connection_states[connection_id] = next_state

    return (C_M, S_M)

def find_reachable_states(M, state, depth):
    visited_states = []

    def _find(M, state, depth):
        if depth == 0 or state in visited_states:
            return set()
        visited_states.append(state)
        reachable = set(np.where(M[state] > 0)[0])
        for reach_state in reachable:
            sub_states = find_reachable_states(M, reach_state, depth - 1)
            reachable = reachable.union(sub_states)
        return reachable

    return _find(M, state, depth)

def render_state_diagram(C_M, S_M, filename, depth=None):
    tot_M = C_M + S_M

    if depth:
        reachable_states = find_reachable_states(tot_M, len(tot_M) - 1, depth)
        reachable_states.add(len(tot_M) - 1)
    else:
        reachable_states = range(len(tot_M))

    graph = Dot(graph_type='digraph', rankdir='LR')
    nodes = [Node(str(i), shape='circle') for i in range(len(tot_M) + 1)]
    nodes[-2].set_shape('point')
    nodes[-1].set_shape('doublecircle')

    for i in reachable_states:
        graph.add_node(nodes[i])
    graph.add_node(nodes[-1])

    def _render_edges(M, color, end_state):
        for i in reachable_states:
            row_sum = sum(tot_M[i])
            col_sum = sum(tot_M[:,i])
            if not end_state:
                for j in reachable_states:
                    elem = M[i,j]
                    if elem > 0:
                        if col_sum > 0:
                            prob = elem / col_sum
                        else:
                            prob = elem / row_sum
                        edge = Edge(nodes[i], nodes[j], label='%.2f' % prob, color=color)
                        graph.add_edge(edge)
            else:
                if row_sum < col_sum:
                    prob = (col_sum - row_sum) / col_sum
                    edge = Edge(nodes[i], nodes[-1], label='%.2f' % prob, color=color)
                    graph.add_edge(edge)

    _render_edges(C_M, 'blue', False)
    _render_edges(S_M, 'red', False)
    _render_edges(None, 'black', True)

    graph.write_png(filename)

