import numpy as np

from itertools import product

global_precedences = [
    ('global', 'lengths'),
    ('stream', 'incrementals'),
    ('global', 'numbers'),
    ('global', 'uniforms'),
    ('global', 'flags'),
    ('global', 'constants'),
    ('connection', 'constants'),
    ('stream', 'constants'),
]

cluster_precedences = [
    'lengths',
    'incrementals',
    'numbers',
    'uniforms',
    'flags',
    'constants',
]

scope_prefix = {
    'global':       'GLO',
    'connection':   'CON',
    'stream':       'STR',
    'cluster':      'CLU',
    'n/a':          '',
}

type_symbols = {
    'lengths':      'LEN',
    'incrementals': 'INC',
    'numbers':      'NUM',
    'uniforms':     'UNI',
    'flags':        'FLA',
    'constants':    'CON',
    'unknown':      'UNK',
}

class Field(object):
    def __init__(self, offset, length, scope, type_):
        self.offset = offset
        self.length = length
        if type(scope) is str:
            self.scope = scope
        else:
            self.scope = 'cluster'
        self.type   = type_

def create_fields(order, estimations, length):
    fields = []
    occupied = np.asarray(length * [None])
    for ((scope, type_), size) in order:
        est = estimations[scope][type_][size]
        for (i, b) in enumerate(est):
            if b:
                off = size * i
                fields.append(Field(off, size, scope, type_))
                occupied[off:off+size] = np.ones(size, dtype=bool)

    for (offset, byte) in enumerate(occupied):
        if not byte:
            fields.append(Field(offset, 1, 'n/a', 'unknown'))

    return fields

def create_global_fields(estimations, sizes):
    global_order = list(product(global_precedences, sizes))
    min_len = len(estimations['global']['constants'][1])
    fields = create_fields(global_order, estimations, min_len)
    return fields

def create_cluster_fields(estimations, sizes, label):
    cluster_order = list(product(product([label], cluster_precedences), sizes))
    min_len = len(estimations[label]['constants'][1])
    fields = create_fields(cluster_order, estimations, min_len)
    return fields

def print_fields(fields):
    output      = []
    occupied    = []
    for field in fields:
        off     = field.offset
        len_    = field.length
        if not np.any(occupied[off:off+len_]):
            diff = (off + len_) - len(occupied)
            if diff > 0:
                occupied.extend(diff * [False])
            output.append(field)
            occupied[off:off+len_] = len_ * [True]

    output.sort(key=lambda f: f.offset)
    msg = '0' + 30 * ' ' + '32' + '\n ' + 31 * '_' + '\n'
    count = 0
    for field in output:
        field_label = scope_prefix[field.scope]
        field_label += '_' if field_label else ''
        field_label += type_symbols[field.type]
        msg += '|' + field_label.center(field.length * 8 - 1)
        count += field.length
        if count % 4 == 0:
            msg += '|\n ' + 31 * '-' + '\n'
    diff = count % 4
    if diff != 0:
        msg += '|\n ' + (31 - 8 * (4 - diff)) * '-' + '\n'
    print msg

