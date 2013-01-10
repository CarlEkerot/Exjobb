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

conn = dict()
out = []

def load_pcap(filename):
    p = pcap.pcapObject()
    p.open_offline(filename)
    p.dispatch(-1, process_eth)
    # flush conn
    for src in conn:
        out.append(conn[src])

def process_eth(length, eth_data, timestamp):
    # extract source address, destination address, protocol
    eth_type = eth_data[12:14]
    ip_data = eth_data[14:]
    if eth_type == ether_type['IPv4']:
        header_len = 4 * (get_byte(ip_data[0]) & 0x0f)
        tot_len = get_short(ip_data[2:4])
        pld_len = tot_len - header_len
        ip_type = ip_data[9]
        src = ip_data[12:16]
        dst = ip_data[16:20]
        pld = ip_data[header_len:tot_len]
        if ip_type == ip_protocol['TCP']:
            process_tcp(timestamp, src, dst, pld_len, pld)
        elif ip_type == ip_protocol['UDP']:
            process_udp(timestamp, src, dst, pld_len, pld)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

def process_tcp(timestamp, src, dst, length, data):
    # check PSH flag; if not set add data to buffer else flush buffer and return its contents
    offset = (get_byte(data[12]) & 0xf0) >> 4
    seq = get_word(data[4:8])
    ack = get_word(data[8:12])
    pld = data[4*offset:]
    if pld:
        if not src in conn:
            conn[src] = (None, [])
        (buf_mdata, buf_data) = conn[src]
        if not buf_mdata:
            buf_mdata = (timestamp, src, dst, seq, ack)
        offset = seq - buf_mdata[3]
        buf_data[offset:offset+len(pld)] = list(pld)
        conn[src] = (buf_mdata, buf_data)
    if src in conn and conn[src][0] and ack != conn[src][0][4]:
        out.append(conn[src])
        del conn[src]

def process_udp(timestamp, src, dst, length, data):
    pass

def get_byte(data):
    return struct.unpack('!B', data)[0]

def get_short(data):
    return struct.unpack('!H', data)[0]

def get_word(data):
    return struct.unpack('!I', data)[0]

def validate_tcp_checksum(length, src, dst, data):
    csum = get_short(data[16:18])
    data = list(data)
    data[16:18] = '\x00\x00'
    if len(data) % 2 != 0:
        data.append('\x00')
    sum = 0
    sum += get_short(src[0:2])
    sum += get_short(src[2:4])
    sum += get_short(dst[0:2])
    sum += get_short(dst[2:4])
    sum += 0x0006
    sum += length
    for i in range(0, len(data), 2):
        sum += get_short(data[i] + data[i+1])
    while sum >> 16:
        sum = (sum & 0xffff) + (sum >> 16)
    return ~sum & 0xffff == csum

def bytes_to_address(bytes_):
    bytes_ = map(lambda x: str(get_byte(x)), bytes_)
    return '.'.join(bytes_)

load_pcap(sys.argv[1])

for m in out:
    (mdata, data) = m
    (ts, src, dst, seq, ack) = mdata
    data = "".join(data)
    print(time.ctime(ts), bytes_to_address(src), bytes_to_address(dst), seq, data)
    print("=========================================================================")
