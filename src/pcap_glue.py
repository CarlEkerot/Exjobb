from pcap_reassembler import load_pcap
from message import Message

def build_messages(filename):
    packets = load_pcap(filename, strict=True)
    packets = filter(lambda x: x.payload[4:8] == '\xffSMB', packets)

    messages            = []
    connection_ids      = {}
    stream_ids          = {}
    next_connection_id  = 0
    next_stream_id      = 0

    for p in packets:
        src_socket = (p.src_addr, p.src_port)
        dst_socket = (p.dst_addr, p.dst_port)
        sockets    = (src_socket, dst_socket)
        if sockets not in connection_ids:
            connection_ids[sockets]         = next_connection_id
            connection_ids[sockets[::-1]]   = next_connection_id
            next_connection_id += 1
        if sockets not in stream_ids:
            stream_ids[sockets] = next_stream_id
            next_stream_id += 1
        conn_id     = connection_ids[sockets]
        stream_id   = stream_ids[sockets]
        msg = Message(p.payload, conn_id, stream_id)
        messages.append(msg)

    return messages

