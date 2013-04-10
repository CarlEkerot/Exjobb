#! /usr/bin/env python

import pcap_glue
import protocol_analyser
import pcap_reassembler

packets = pcap_reassembler.load_pcap('../cap/dns-30628-packets.pcap', strict=True)
nums = [p.number for p in packets]
truth = []
with open('../cap/dns.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        if int(no) in nums:
            truth.append(type_[:-1])

msgs = pcap_glue.build_messages('../cap/dns-30628-packets.pcap')
an = protocol_analyser.ProtocolAnalyser(msgs[:10000], 100, truth[:10000])
an.cluster(200, max_num_types=10)
#an.state_inference('dns-state_diagram.png', 5)
#an.classify_fields()

