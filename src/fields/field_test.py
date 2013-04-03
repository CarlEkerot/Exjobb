#! /usr/bin/env python

import pcap_reassembler
import pickle

from field_classifier import classify_fields

size = 20000

packets = pcap_reassembler.load_pcap('../../cap/smb-only.cap', strict=True)
packets = filter(lambda x: x.payload[4:8] == '\xffSMB', packets)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/dns-30628-packets.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/tftp.pcap', strict=True)[:size]
# packets = pcap_reassembler.load_pcap('../../cap/utp-fixed.pcap',
#         layer=pcap_reassembler.NETWORK_LAYER)

filename = '/media/data/smb/smb-20000-200-50-0.75-0.40'
with open(filename + '.fdl') as f:
    labels = pickle.load(f)

(global_est, cluster_est) = classify_fields(packets, labels, 200)

with open('%s.est' % filename, 'w') as f:
    pickle.dump(dict(global_est), f)
with open('%s.cest' % filename, 'w') as f:
    pickle.dump(dict(cluster_est), f)

