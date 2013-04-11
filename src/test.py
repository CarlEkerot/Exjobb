#! /usr/bin/env python

import pcap_glue
import protocol_analyser
import pcap_reassembler

packets = pcap_reassembler.load_pcap('../cap/dns-30628-packets.pcap', strict=True)
msgs = pcap_glue.build_messages('../cap/dns-30628-packets.pcap')
an = protocol_analyser.ProtocolAnalyser(msgs[:5000], 100)
an.cluster(200, max_num_types=10)
#an.state_inference('dns-state_diagram.png', 5)
#an.classify_fields()

