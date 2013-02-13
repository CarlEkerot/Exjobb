#! /usr/bin/env python

import pcap_reassembler
import cluster
import collections

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)

clusters = cluster.cluster(packets, 2000, 0.2, 3)

# Get the actual types of each packet
type_dict = {}
types = []
count = 0
real_type = []
with open('../../cap/smb-only.csv') as f:
    f.readline()
    for line in f:
        cols = line.split('","')
        prot = cols[4]
        type_ = cols[-1].split(',')[0]
        real_type.append(cols[-1])
        if prot == 'SMB' and type_ not in type_dict:
            type_dict[type_] = count
            count += 1
        try:
            types.append(type_dict[type_])
        except:
            types.append(-1)

# Output the different types in each cluster
for label in clusters:
    s = set()
    d = collections.defaultdict(lambda: 0)
    for i in clusters[label]:
        s.add(types[i])
        d[types[i]] += 1
    print 'Cluster ' + str(int(label)) + ": "
    for t in s:
        print d[t], real_type[t][:-2]
    print ""
