#! /usr/bin/env python

import pcap_glue
import protocol_analyser
import pcap_reassembler

packets = pcap_reassembler.load_pcap('/media/data/cap/smb-only.cap', strict=True)
packets = [p for p in packets if p.payload[4:8] == '\xffSMB']
nums = [p.number for p in packets]
truth = []
with open('/media/data/cap/smb-only.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        if int(no) in nums:
            truth.append(type_[:-1])

msgs = pcap_glue.build_messages('/media/data/cap/smb-only.cap')
an = protocol_analyser.ProtocolAnalyser(msgs[:20000], 200, truth)
an.cluster(10, max_num_types=100)
an.state_inference('smb-state_diagram.png', 5)
an.classify_fields()

