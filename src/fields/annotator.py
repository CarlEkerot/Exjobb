#! /usr/bin/env python

import numpy as np

from lxml import etree
from collections import defaultdict

with open('../../cap/dns.xml') as f:
    tree = etree.parse(f)

dns_fields = {
    'dns.id':               'UNIFORM',
    'dns.flags':            'FLAG',
    'dns.count.queries':    'NUMBER',
    'dns.count.answers':    'NUMBER',
    'dns.count.auth_rr':    'NUMBER',
    'dns.count.add_rr':     'NUMBER',
    'dns.qry.name':         'SPECIAL',
    'dns.qry.type':         'FLAG',
    'dns.qry.class':        'FLAG',
    'dns.resp.name':        'SPECIAL',
    'dns.resp.type':        'FLAG',
    'dns.resp.class':       'FLAG',
    'dns.resp.ttl':         'NUMBER',
    'dns.resp.len':         'NUMBER',
    'dns.resp.addr':        'UNIFORM',
    'dns.resp.ns':          'SPECIAL',
}

#[field][field_no][byte_pos]
samples = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: np.zeros(256))))

fields = tree.xpath('//field')
for field in fields:
    name = field.get('name')
    if name in dns_fields:
        type_ = dns_fields[name]
        value = field.get('value')
        bytes_ = map(lambda (c1, c2): int(c1 + c2, 16), zip(value[::2], value[1::2]))
        if type_ != 'SPECIAL':
            for (i, byte) in enumerate(bytes_):
                samples[name][0][i][byte] += 1
        else:
            field_num = 0
            label_len = 0
            byte_pos = 0
            for byte in bytes_:
                samples[name][field_num][byte_pos][byte] += 1
                if label_len > 0:
                    # ascii
                    byte_pos += 1
                    label_len -= 1
                    if label_len == 0:
                        byte_pos = 0
                        field_num += 1
                elif (byte >> 6) != 0b11:
                    # length
                    label_len = byte
                    field_num += 1
                else:
                    # pointer
                    byte_pos += 1

import matplotlib.pyplot as plt
plt.bar(range(256), samples['dns.qry.name'][0][0])
plt.xlim(0, 255)
plt.show()

# normalize the samples

