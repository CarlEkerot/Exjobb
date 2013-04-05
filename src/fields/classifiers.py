import numpy as np

from features import *
from struct import unpack
from ransac import LineModel, ransac

__all__ = [
    'constant',
    'flag',
    'uniform',
    'number',
    'incremental',
    'length',
]

number_threshold    = 1.2
uniform_threshold   = 0.6

_model = LineModel()

def constant(samples, size):
    fields = []
    for i in range(0, len(samples) - size + 1, size):
        consts  = samples[i:i+size,CONSTANT]
        success = np.all(consts)
        fields.append(success)
    return fields

def flag(samples, size, max_num_values):
    fields = []
    for i in range(0, len(samples) - size + 1, size):
        flags    = samples[i:i+size,FLAG]
        min_vals = np.all(flags > 1)
        max_vals = np.all(flags < max_num_values)
        success  = min_vals & max_vals
        fields.append(success)
    return fields

def uniform(samples, size):
    fields = []
    for i in range(0, len(samples) - size + 1, size):
        unifs   = samples[i:i+size,UNIFORM]
        success = np.all(unifs <= uniform_threshold)
        fields.append(success)
    return fields

def number(samples, size, zero_ratio=0.1):
    fields = []
    for i in range(0, len(samples) - size + 1, size):
        consts  = samples[i:i+size,CONSTANT].astype(bool)
        zeros   = samples[i:i+size,ZERO]
        unifs   = samples[i:i+size,UNIFORM]
        nums    = samples[i:i+size,NUMBER]
        found = np.where((nums < number_threshold) & ~consts)[0].tolist()
        if not found:
            fields.append(False)
            continue
        center = found[0]
        success = np.all(zeros[:center] == 1.0)
        if center != size - 1:
            success = success and zeros[center] >= zero_ratio
            success = success and np.all(unifs[center+1:] <= uniform_threshold)
        fields.append(success)
    return fields

def incremental(msgs, size, incr_ratio=0.99):
    fields = []
    for i in range(0, len(msgs[0]) - size + 1, size):
        prev_value = -1
        count = 0
        for msg in msgs:
            value = _get_value_from_bytes(msg[i:i+size])
            if value > prev_value:
                count += 1
            prev_value = value
        success = 1 < count >= incr_ratio * len(msgs)
        fields.append(success)
    return fields

def length(msgs, size, noise_ratio, num_iters, eps=1e-10):
    fields = []
    min_size = min(map(len, msgs))
    for i in range(0, min_size - size + 1, size):
        X = [_get_value_from_bytes(msg[i:i+size]) for msg in msgs]
        Y = [len(msg) for msg in msgs]
        data = np.asarray([X, Y]).T

        try:
            (params, _, res) = ransac(data, _model, 2, (1 - noise_ratio), num_iters, eps)
            k = params[0]
            m = params[1]
            success = k > (1 - eps) and m > -eps
        except ValueError:
            success = False

        fields.append(success)

    return fields

def _get_value_from_bytes(data):
    value = 0
    for byte in data:
        value = (value << 8) + byte
    return value

