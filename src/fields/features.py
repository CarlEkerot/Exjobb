from __future__ import division

import copy
import numpy as np

from scipy.stats import norm

__all__ = [
    'CONSTANT',
    'ZERO',
    'FLAG',
    'UNIFORM',
    'NUMBER',
    'get_features',
]

CONSTANT    = 0
ZERO        = 1
FLAG        = 2
UNIFORM     = 3
NUMBER      = 4

class Feature(object):
    pass

class ConstantFeature(Feature):
    def get_value(self, dist):
        constant = 1 if len(np.where(dist == 0)[0]) == 255 else 0
        return constant

class ZeroFeature(Feature):
    def get_value(self, dist):
        dist = copy.deepcopy(dist)
        dist /= np.linalg.norm(dist, ord=1)
        ratio = dist[0]
        return ratio

class FlagFeature(Feature):
    def get_value(self, dist):
        thres = sum(dist) * 0.9
        sort_dist = sorted(dist, reverse=True)
        sum_ = 0
        for i, b in enumerate(sort_dist):
            sum_ += b
            if sum_ >= thres:
                break
        return i + 1

class UniformFeature(Feature):
    def get_value(self, dist):
        dist = copy.deepcopy(dist)
        dist /= np.linalg.norm(dist, ord=1)
        med = np.median(dist)
        deviation = sum([abs(f - med) for f in dist])
        return deviation

class NumberFeature(Feature):
    def get_value(self, dist):
        dist = copy.deepcopy(dist)
        samples = []
        for (i, count) in enumerate(dist):
            samples.extend(count * [i])
        (mu, sigma) = norm.fit(samples)
        sigma = max(sigma, 0.6)
        sigma = min(sigma, 20)
        dist /= np.linalg.norm(dist, ord=1)
        deviation = sum(abs(dist[i] - norm.pdf(i, loc=mu, scale=sigma)) for i in range(256))
        return deviation

feature_functions = [
    ConstantFeature(),
    ZeroFeature(),
    FlagFeature(),
    UniformFeature(),
    NumberFeature(),
]

def get_features(dist, constant, zero, flag, uniform, number):
    feature_list = len(feature_functions) * [0]
    indices     = [CONSTANT, ZERO, FLAG, UNIFORM, NUMBER]
    activated   = [constant, zero, flag, uniform, number]
    for (index, active) in zip(indices, activated):
        feature_list[index] = feature_functions[index].get_value(dist) if active else 0
    return feature_list

