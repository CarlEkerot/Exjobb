#! /usr/bin/env python

import pcap_glue
import protocol_analyser
import pcap_reassembler

GLOBAL_CONSTANT     = 0
GLOBAL_FLAG         = 1
GLOBAL_UNIFORM      = 2
GLOBAL_NUMBER       = 3
GLOBAL_LENGTH       = 4
CONNECTION_CONSTANT = 5
STREAM_CONSTANT     = 6
STREAM_INCREMENTAL  = 7
DATA                = 8
UNKNOWN             = 9

definition_mapping = {
    ('global', 'constants'):        GLOBAL_CONSTANT,
    ('global', 'flags'):            GLOBAL_FLAG,
    ('global', 'uniforms'):         GLOBAL_UNIFORM,
    ('global', 'numbers'):          GLOBAL_NUMBER,
    ('global', 'lengths'):          GLOBAL_LENGTH,
    ('connection', 'constants'):    CONNECTION_CONSTANT,
    ('stream', 'constants'):        STREAM_CONSTANT,
    ('stream', 'incrementals'):     STREAM_INCREMENTAL,
    ('n/a', 'unknown'):             UNKNOWN,
}

definition = [
    (GLOBAL_UNIFORM, 16),
    (GLOBAL_FLAG, 9),
    (GLOBAL_CONSTANT, 3),
    (GLOBAL_FLAG, 4),
    (GLOBAL_NUMBER, 16),
    (GLOBAL_NUMBER, 16),
    (GLOBAL_NUMBER, 16),
    (GLOBAL_NUMBER, 16),
]

header_bits = sum(t[1] for t in definition)
header_limit = int(round(header_bits / 8.0))
realized_definition = [e for t in definition for e in t[1] * [t[0]]]
print header_bits, header_limit

packets = pcap_reassembler.load_pcap('/media/data/cap/dns-30628-packets.pcap', strict=True)
nums = [p.number for p in packets]
truth = []
with open('/media/data/cap/dns.csv.clean') as f:
    for line in f:
        (no, type_) = line.split(',')
        if int(no) in nums:
            truth.append(type_[:-1])

msgs = pcap_glue.build_messages('/media/data/cap/dns-30628-packets.pcap')
an = protocol_analyser.ProtocolAnalyser(msgs, 200, truth)
an.cluster(200, max_num_types=10, header_limit=header_limit)
fields = an.classify_fields(global_limit=header_limit)
#an.state_inference('dns-state_diagram.png', 5)

# Check the type of each byte
output      = []
occupied    = []
for field in fields:
    off     = field.offset
    len_    = field.length
    if not any(occupied[off:off+len_]):
        diff = (off + len_) - len(occupied)
        if diff > 0:
            occupied.extend(diff * [False])
        output.append(field)
        occupied[off:off+len_] = len_ * [True]
output.sort(key=lambda f: f.offset)

num_correct = 0
pos = 0
for field in output:
    try:
        type_ = definition_mapping[(field.scope, field.type)]
        for i in range(8 * field.length):
            if pos == header_bits: break
            if type_ == realized_definition[pos]:
                num_correct += 1
            pos += 1
    except: pass
print '%d correct bits out of %d' % (num_correct, header_bits)

