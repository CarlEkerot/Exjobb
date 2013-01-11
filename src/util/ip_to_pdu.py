#! /usr/bin/env python

import sys
import pcap
import struct
import time

ether_type = {
    'IPv4': '\x08\x00',
    'IPv6': '\x86\xdd',
}

ip_protocol = {
    'TCP': '\x06',
    'UDP': '\x11',
}

tcp_conn = dict()
msgs = []

def load_pcap(filename):
    p = pcap.pcapObject()
    p.open_offline(filename)
    # process all packets
    p.dispatch(-1, process_eth)
    # flush TCP connections
    for src in tcp_conn:
        tcp_flush(src)
    return msgs

def process_eth(length, data, ts):
    # strips ethernet header
    eth_type = data[12:14]
    pld = data[14:]
    if eth_type == ether_type['IPv4']:
        process_ipv4(ts, pld)
    else:
        raise NotImplementedError

def process_ipv4(ts, data):
    # extract source address, destination address, protocol type
    header_len = 4 * (decode_byte(data[0]) & 0x0f)
    tot_len = decode_short(data[2:4])
    ip_type = data[9]
    src = data[12:16]
    dst = data[16:20]
    pld = data[header_len:tot_len]
    if ip_type == ip_protocol['TCP']:
        process_tcp(ts, src, dst, pld)
    elif ip_type == ip_protocol['UDP']:
        process_udp(ts, src, dst, pld)
    else:
        raise NotImplementedError

def process_tcp(ts, src, dst, data):
    # reassemble PDUs by buffering packets and flushing when ack changes
    offset = (decode_byte(data[12]) & 0xf0) >> 4
    seq = decode_word(data[4:8])
    ack = decode_word(data[8:12])
    pld = data[4*offset:]
    if pld:
        if not src in tcp_conn:
            tcp_conn[src] = (None, [])
        (buf_mdata, buf_data) = tcp_conn[src]
        if not buf_mdata:
            buf_mdata = (ts, src, dst, seq, ack)
        offset = seq - buf_mdata[3]
        buf_data[offset:offset+len(pld)] = list(pld)
        tcp_conn[src] = (buf_mdata, buf_data)
    if src in tcp_conn and tcp_conn[src][0] and ack != tcp_conn[src][0][4]:
        tcp_flush(src)
        del tcp_conn[src]

def tcp_flush(src):
    (mdata, dat) = tcp_conn[src]
    (ts, src, dst, _, _) = mdata
    mdata = (ts, src, dst)
    msgs.append((mdata, dat))

def process_udp(ts, src, dst, data):
    mdata = (ts, src, dst)
    msgs.append((mdata ,data[8:]))

def decode_byte(data):
    return struct.unpack('!B', data)[0]

def decode_short(data):
    return struct.unpack('!H', data)[0]

def decode_word(data):
    return struct.unpack('!I', data)[0]

def validate_tcp_checksum(length, src, dst, data):
    # this is currently unused as we simply insert newer data
    # over old data without checking the checksum
    csum = decode_short(data[16:18])
    data = list(data)
    data[16:18] = '\x00\x00'
    if len(data) % 2 != 0:
        data.append('\x00')
    sum = 0
    sum += decode_short(src[0:2])
    sum += decode_short(src[2:4])
    sum += decode_short(dst[0:2])
    sum += decode_short(dst[2:4])
    sum += 0x0006
    sum += length
    for i in range(0, len(data), 2):
        sum += decode_short(data[i] + data[i+1])
    while sum >> 16:
        sum = (sum & 0xffff) + (sum >> 16)
    return ~sum & 0xffff == csum

def bytes_to_address(bytes_):
    bytes_ = map(lambda x: str(decode_byte(x)), bytes_)
    return '.'.join(bytes_)

out = load_pcap(sys.argv[1])

for m in out:
    (mdata, data) = m
    (ts, src, dst) = mdata
    data = "".join(data)
    print(time.ctime(ts), bytes_to_address(src), bytes_to_address(dst), data)
    print("=========================================================================")
