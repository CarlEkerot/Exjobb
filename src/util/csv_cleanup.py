#! /usr/bin/env python

import sys

filename = sys.argv[1]

with open(filename + '.clean', 'w') as fout:
    with open(filename) as fin:
        fin.readline()
        for line in fin:
            cols = line.split('","')
            no = cols[0][1:]
            prot = cols[4]
            type_ = cols[-1][:-2].split(',')[0]
            #if 'response' in type_:
            #    type_ = 'response'
            #else:
            #    type_ = 'request'
            fout.write('%s,%s\n' % (no, type_))

