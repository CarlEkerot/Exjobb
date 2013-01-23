__all__ = ['UDPClassifier']

class Classifier(object):
    def init(self, msg):
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
