"""ipv4-data

Simply extracts the IPv4 payload from packets in pcap-files.

"""

import sys
import pcap
import struct
import time

# EtherType constants
_ether_type = {
    'IPv4': '\x08\x00',
    'IPv6': '\x86\xdd',
}

# IP protocol field constants
_ip_protocol = {
    'TCP': '\x06',
    'UDP': '\x11',
}

# message buffer
_msgs       = None

def extract_pcap_data(filename):
    """Loads a pcap file and extracts raw data from each of the
    IPv4 packet. Returns a dictionary indexed by the transport layer
    protocol, where each value is the raw data.

    """
    global _msgs
    _msgs = {}
    _msgs['TCP'] = []
    _msgs['UDP'] = []
    p = pcap.pcapObject()
    p.open_offline(filename)
    # process all packets
    p.dispatch(-1, _process_eth)
    
    for prot in _msgs:
        f = open(prot + '.out', 'w')
        for packet_data in _msgs[prot]:
            f.write(packet_data.encode('hex') + '\n')
        f.close()
    return _msgs

def _process_eth(length, data, ts):
    """Processes an Ethernet packet (header to checksum; not the full frame).

    Propagates processing to the correct IP version processing function.

    """
    eth_type = data[12:14]
    pld = data[14:]
    if eth_type == _ether_type['IPv4']:
        _process_ipv4(ts, pld)
    else:
        raise NotImplementedError

def _process_ipv4(ts, data):
    """Processes an IPv4 packet.

    Extracts the packet data and puts it in the global protocol-indexed
    dictionary.

    """
    header_len = 4 * (_decode_byte(data[0]) & 0x0f)
    tot_len = _decode_short(data[2:4])
    ip_type = data[9]
    pld = data[header_len:tot_len]
    if ip_type == _ip_protocol['TCP']:
        _msgs['TCP'].append(pld)
    elif ip_type == _ip_protocol['UDP']:
        _msgs['UDP'].append(pld)
    else:
        raise NotImplementedError

def _decode_byte(data):
    """Decodes one byte of network data into an unsigned char."""
    return struct.unpack('!B', data)[0]

def _decode_short(data):
    """Decodes two bytes of network data into an unsigned short."""
    return struct.unpack('!H', data)[0]

