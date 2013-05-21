from __future__ import division

import copy
import numpy as np

__all__ = [
    'CONSTANT',
    'ZERO',
    'FLAG',
    'UNIFORM',
    'get_features',
]

CONSTANT    = 0
ZERO        = 1
FLAG        = 2
UNIFORM     = 3

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
        num = len(np.where(dist > 0)[0])
        return num

class UniformFeature(Feature):
    def get_value(self, dist):
        dist = copy.deepcopy(dist)
        dist /= np.linalg.norm(dist, ord=1)
        deviation = sum([abs(f - 1 / 256) for f in dist])
        return deviation

feature_functions = [
    ConstantFeature(),
    ZeroFeature(),
    FlagFeature(),
    UniformFeature(),
]

def get_features(dist, constant, zero, flag, uniform):
    feature_list = len(feature_functions) * [0]
    indices     = [CONSTANT, ZERO, FLAG, UNIFORM]
    activated   = [constant, zero, flag, uniform]
    for (index, active) in zip(indices, activated):
        feature_list[index] = feature_functions[index].get_value(dist) if active else 0
    return feature_list

