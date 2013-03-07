__all__ = ['UDPClassifier', 'TCPClassifier', 'DNSClassifier']

class Classifier(object):
    def __init__(self, msg):
        self._msg = msg
        self._init_boundaries()

    def _init_boundaries(self):
        raise NotImplementedError

    def is_boundary(self, pos):
        assert(not self._boundaries == None)
        return pos in self._boundaries

class UDPClassifier(Classifier):
    def _init_boundaries(self):
        self._boundaries = [1, 3, 5, 7, len(self._msg) - 1]

class TCPClassifier(Classifier):
    def _init_boundaries(self):
        self._boundaries = [1, 3, 7, 11, 12, 13, 15, 17, 19]
        offset = ord(self._msg[12]) >> 4
        if offset > 5:
            self._boundaries.append(4 * offset - 1)
        self._boundaries.append(len(self._msg) - 1)

class DNSClassifier(Classifier):
    def _init_boundaries(self):
        self._boundaries = [1, 3, 5, 7, 9, 11, len(self._msg) - 1]
