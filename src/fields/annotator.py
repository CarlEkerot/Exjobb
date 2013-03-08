#! /usr/bin/env python

from __future__ import division

import pcap_reassembler
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

classes = {
    'FLAG': 0,
    'NUMBER': 1,
    'ASCII': 2,
    'UNIFORM': 3,
}

classes_rev = [
    'FLAG',
    'NUMBER',
    'ASCII',
    'UNIFORM',
]

X = []
y = []
names = []
for name in samples:
    fields = samples[name]
    for field_num in fields:
        field = fields[field_num]
        for byte_pos in field:
            features = field[byte_pos]
            type_ = dns_fields[name]
            if type_ != 'SPECIAL':
                class_ = classes[type_]
            else:
                class_ = classes['NUMBER'] if (field_num % 2) == 0 else classes['ASCII']
            X.append(features)
            y.append(class_)
            names.append(name)
from sklearn.preprocessing import normalize
X = normalize(X, norm='l1', axis=0)

#import matplotlib.pyplot as plt
#for i in range(0, 10):
#    print names[i], y[i]
#    plt.bar(range(256), X[i])
#    plt.xlim(0, 255)
#    plt.show()

from sklearn.svm import SVC
clf = SVC(C=1.0, gamma=0.0, probability=True)
clf.fit(X, y)
#pred = clf.predict_proba(X)
#
#correct = 0
#for i in range(len(X)):
#    if np.argmax(pred[i]) == y[i]:
#        correct += 1
#print '%d correct out of %d (%.2f%%)' % (correct, len(X), 100 * correct / len(X))

#print classes_rev
#for i in range(40):
#    print pred[i], classes_rev[y[i]], names[i]

limit = 200

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)

global_msgs = [p.data[:limit] for p in packets]
GP = np.zeros((limit, 256))
for msg in global_msgs:
    for (pos, val) in enumerate(msg):
        GP[pos,ord(val)] += 1
GP = normalize(GP, norm='l1', axis=0)

pred = clf.predict_proba(GP)
print classes_rev
print pred

