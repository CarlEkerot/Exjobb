from itertools import product

global_precedences = [
    ('global', 'constants'),
    ('connection', 'constants'),
    ('stream', 'constants'),
    ('global', 'lengths'),
    ('stream', 'incrementals'),
    ('global', 'numbers'),
    ('global', 'uniforms'),
    ('global', 'flags'),
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
    'type_distinguisher':   'TD',
    'lengths':              'LEN',
    'incrementals':         'INC',
    'numbers':              'NUM',
    'uniforms':             'UNI',
    'flags':                'FLA',
    'constants':            'CON',
    'unknown':              'UNK',
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

def create_fields(order, estimations, tds=None):
    fields      = []
    occupied    = []
    if tds:
        occupied = (max(tds) + 1) * [False]
        for pos in tds:
            fields.append(Field(pos, 1, 'n/a', 'type_distinguisher'))
            occupied[pos] = True
    for ((scope, type_), size) in order:
        est = estimations[scope][type_][size]
        for (i, b) in enumerate(est):
            off = size * i
            diff = (off + size) - len(occupied)
            if diff > 0:
                occupied.extend(diff * [False])
            if b:
                fields.append(Field(off, size, scope, type_))
                occupied[off:off+size] = size * [True]

    for (offset, byte) in enumerate(occupied):
        if not byte:
            fields.append(Field(offset, 1, 'n/a', 'unknown'))

    return fields

def create_global_fields(estimations, sizes):
    global_order = list(product(global_precedences, sizes))
    fields = create_fields(global_order, estimations)
    return fields

def create_cluster_fields(estimations, sizes, label, type_distinguishers):
    cluster_order = list(product(product([label], cluster_precedences), sizes))
    fields = create_fields(cluster_order, estimations, type_distinguishers)
    return fields

def print_fields(fields, limit=None):
    output      = []
    occupied    = []
    for field in fields:
        off     = field.offset
        len_    = field.length
        if not any(occupied[off:off+len_]):
            diff = (off + len_) - len(occupied)
            if diff > 0:
                occupied.extend(diff * [False])
            output.append(field)
            occupied[off:off+len_] = len_ * [True]

    output.sort(key=lambda f: f.offset)
    msg = '0' + 30 * ' ' + '32' + '\n ' + 31 * '_' + '\n'
    count = 0
    for field in output:
        if limit and count == limit:
            break
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

