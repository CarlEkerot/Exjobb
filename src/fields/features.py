__all__ = [
    'ConstantFeature',
    'AsciiFeature',
    'UniformFeature',
    'NumberFeature',
]

import numpy as np

from string import printable
from scipy.stats import norm

class Feature(object):
    pass

class ConstantFeature(Feature):
    def get_values(self, dist):
        constant = 1 if len(np.where(dist == 0)[0]) == 255 else 0
        return [constant]

class AsciiFeature(Feature):
    def get_values(self, dist):
        num_ascii = sum([f for (b, f) in enumerate(dist) if b in map(ord, printable)])
        return [num_ascii]

class UniformFeature(Feature):
    def get_values(self, dist):
        med = np.median(dist)
        deviation = sum([abs(f - med) for f in dist])
        return [deviation]

class NumberFeature(Feature):
    def __init__(self):
        nor = norm(10 * range(256), 256 * np.linspace(1, 20, 10).tolist())
        self.pdf = np.asarray([nor.pdf(i) for i in range(256)])

    def get_values(self, dist):
        deviation = float('inf')
        for param in range(256 * 10):
            dev = sum(abs(dist[b] - self.pdf[b,param]) for b in range(256))
            if dev < deviation:
                deviation = dev
            print param
        return [deviation]

