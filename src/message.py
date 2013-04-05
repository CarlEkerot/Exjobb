class Message(object):
    def __init__(self, data, conn, stream):
        self.data   = data
        self.conn   = conn
        self.stream = stream

