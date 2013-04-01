#! /usr/bin/env python

import pickle
import numpy as np

from itertools import product

class Field(object):
    def __init__(self, offset, length, type_):
        self.offset = offset
        self.length = length
        self.type   = type_

def create_fields(order, estimations, length):
    fields = []
    occupied = np.asarray(length * [None])
    for (type_, size) in order:
        est = estimations[type_][size]
        for (i, b) in enumerate(est):
            offset = size * i
            if b:
                fields.append(Field(offset, size, type_))
                occupied[offset:offset+size] = np.ones(size, dtype=bool)

    for (offset, byte) in enumerate(occupied):
        if not byte:
            fields.append(Field(offset, 1, 'unknown'))

    return fields

def print_fields(fields, symbols, length):
    output = []
    occupied = np.asarray(length * [None])
    for field in fields:
        if not np.any(occupied[field.offset:field.offset+field.length]):
            output.append(field)
            occupied[field.offset:field.offset+field.length] = np.ones(field.length, dtype=bool)

    output.sort(key=lambda f: f.offset)
    msg = '0' + 30 * ' ' + '32' + '\n ' + 31 * '_' + '\n'
    count = 0
    for field in output:
        msg += '|' + symbols[field.type].center(field.length * 8 - 1)
        count += field.length
        if count % 4 == 0:
            msg += '|\n ' + 31 * '-' + '\n'
    diff = count % 4
    if diff != 0:
        msg += '|\n ' + (31 - 8 * (4 - diff)) * '-' + '\n'
    print msg

global_precedences = [
    'global_lengths',
    'stream_incrementals',
    'global_numbers',
    'global_uniforms',
    'global_flags',
    'global_constants',
    'connection_constants',
    'stream_constants',
]

cluster_precedences = [
    'numbers',
    'uniforms',
    'flags',
    'constants',
]

sizes = [4, 2, 1]

global_symbols = {
    'global_lengths':       'G_L',
    'stream_incrementals':  'S_I',
    'global_numbers':       'G_N',
    'global_uniforms':      'G_U',
    'global_flags':         'G_F',
    'global_constants':     'G_C',
    'connection_constants': 'C_C',
    'stream_constants':     'S_C',
    'unknown':              'U',
}

cluster_symbols = {
    'numbers':      'NUM',
    'uniforms':     'UNI',
    'flags':        'FLA',
    'constants':    'CON',
    'unknown':      'UNK',
}

global_order = list(product(global_precedences, sizes))
cluster_order = list(product(cluster_precedences, sizes))

filename = '/media/data/smb/smb-20000-200-50-0.75-0.40'

with open(filename + '.est') as f:
    estimations = pickle.load(f)
with open(filename + '.cest') as f:
    cluster_estimations = pickle.load(f)

print ' GLOBAL '.center(33, '=')
min_len = len(estimations['global_constants'][1])
fields = create_fields(global_order, estimations, min_len)
print_fields(fields, global_symbols, min_len)
for label in cluster_estimations:
    print (' CLUSTER %d ' % label).center(33, '=')
    min_len = len(cluster_estimations[label]['constants'][1])
    fields = create_fields(cluster_order, cluster_estimations[label], min_len)
    print_fields(fields, cluster_symbols, min_len)

