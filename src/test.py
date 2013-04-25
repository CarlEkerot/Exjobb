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

msgs = pcap_glue.build_messages('../cap/dhcp.pcap')
an = protocol_analyser.ProtocolAnalyser(msgs[:5000], 30, truth[:5000])
an.cluster(500, max_num_types=10)
#an.state_inference('dns-state_diagram.png', 5)
#an.classify_fields()

