from __future__ import division

__all__ = [
    'ConstantFeature',
    'FlagFeature',
    'AsciiFeature',
    'UniformFeature',
    'NumberFeature',
]

import copy
import numpy as np

from string import printable
from scipy.stats import norm

class Feature(object):
    pass

class ConstantFeature(Feature):
    def get_values(self, dist):
        constant = 1 if len(np.where(dist == 0)[0]) == 255 else 0
        return [constant]

class FlagFeature(Feature):
    def get_values(self, dist):
        thres = sum(dist) * 0.9
        sort_dist = sorted(dist, reverse=True)

        sum_ = 0
        for i, b in enumerate(sort_dist):
            sum_ += b
            if sum_ >= thres:
                break

        return [i+1]

class AsciiFeature(Feature):
    def get_values(self, dist):
        dist = copy.deepcopy(dist)
        dist /= np.linalg.norm(dist, ord=1)

        num_ascii = sum([f for (b, f) in enumerate(dist) if b in map(ord, printable)])
        return [num_ascii]

class UniformFeature(Feature):
    def get_values(self, dist):
        dist = copy.deepcopy(dist)
        dist /= np.linalg.norm(dist, ord=1)

        med = np.median(dist)
        deviation = sum([abs(f - med) for f in dist])

        return [deviation]

class NumberFeature(Feature):
    def get_values(self, dist):
        dist = copy.deepcopy(dist)

        samples = []
        for (i, count) in enumerate(dist):
            samples.extend(count * [i])
        (mu, sigma) = norm.fit(samples)
        sigma = max(sigma, 0.6)
        sigma = min(sigma, 20)

        dist /= np.linalg.norm(dist, ord=1)

        deviation = sum(abs(dist[i] - norm.pdf(i, loc=mu, scale=sigma)) for i in range(256))

        return [deviation]

