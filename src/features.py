__all__ = ['PositionFeature', 'DataFeature', 'PredecessorFeature', 'SuccessorFeature']

class Feature(object):
    def __init__(self, type_, size):
        self.type_ = type_
        self.size = size

    def get_value(self, msg, pos):
        raise NotImplementedError

class PositionFeature(Feature):
    def __init__(self):
        super(PositionFeature, self).__init__(type_='numeric', size=1)

    def get_value(self, msg, pos):
        return pos + 1

class DataFeature(Feature):
    def __init__(self):
        super(DataFeature, self).__init__(type_='nominal', size=256)

    def get_value(self, msg, pos):
        return ord(msg[pos])

class PredecessorFeature(Feature):
    def __init__(self):
        super(PredecessorFeature, self).__init__(type_='nominal', size=257)

    def get_value(self, msg, pos):
        if pos > 0:
            pred = ord(msg[pos-1])
        else:
            pred = 256
        return pred

class SuccessorFeature(Feature):
    def __init__(self):
        super(SuccessorFeature, self).__init__(type_='nominal', size=257)

    def get_value(self, msg, pos):
        if pos < len(msg) - 1:
            succ = ord(msg[pos+1])
        else:
            succ = 256
        return succ

