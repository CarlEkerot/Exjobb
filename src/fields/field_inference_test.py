#! /usr/bin/env python

import pickle

from field_inference import create_global_fields, create_cluster_fields, print_fields

sizes = [4, 2, 1]

filename = '/media/data/smb/smb-20000-200-50-0.75-0.40'

with open(filename + '.est') as f:
    estimations = pickle.load(f)
with open(filename + '.cest') as f:
    cluster_estimations = pickle.load(f)

print ' GLOBAL '.center(33, '=')
fields = create_global_fields(estimations, sizes)
print_fields(fields)
for label in cluster_estimations:
    print (' CLUSTER %d ' % label).center(33, '=')
    fields = create_cluster_fields(cluster_estimations, sizes, label)
    print_fields(fields)

