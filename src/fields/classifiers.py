import numpy as np

from features import *
from struct import unpack
from ransac import LineModel, ransac
from collections import defaultdict
from scipy.stats import norm


__all__ = [
    'constant',
    'flag',
    'uniform',
    'number',
    'incremental',
    'length',
]

number_threshold    = 0.9
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

def number(msgs, size, resolution=256):
    fields = []
    for i in range(0, len(msgs[0]) - size + 1, size):
        gap_in_data = False
        # Build a distribution and find the maximum and minimum values
        dist = defaultdict(lambda: 0)
        min_value = np.inf
        max_value = -1
        for msg in msgs:
            data = msg[i:i+size]
            if 256 in data:
                gap_in_data = True
                break
            value = _get_value_from_bytes(data)
            if value < min_value:
                min_value = value
            if value > max_value:
                max_value = value
            dist[value] += 1

        if gap_in_data or max_value == min_value:
            fields.append(False)
            continue

        # Create a number of location in which to sample the distribution
        sample_locations = np.linspace(min_value, max_value, resolution)
        samples = []
        for loc in sample_locations:
            samples.extend(dist[int(round(loc))] * [int(round((resolution - 1) * loc / 256**size))])

        # Fit a normal distribution to the samples
        (mu, sigma) = norm.fit(samples)
        sigma = max(sigma, 1)
        sigma = min(sigma, 20)

        # Convert the real distribution into a form that can be
        # compared to the fitted distribution
        dist = np.zeros(resolution)
        for s in samples:
            dist[s] += 1
        dist /= np.linalg.norm(dist, ord=1)

        # Calculate deviation from the fitted normal distribution
        deviation = sum(abs(dist[i] - norm.pdf(i, loc=mu, scale=sigma)) for i in range(resolution))

        success = deviation < number_threshold
        fields.append(success)
    return fields

def incremental(msgs, size, incr_ratio=0.99):
    fields = []
    for i in range(0, len(msgs[0]) - size + 1, size):
        gap_in_data = False
        prev_value = -1
        count = 0
        for msg in msgs:
            data = msg[i:i+size]
            if 256 in data:
                gap_in_data = True
                break
            value = _get_value_from_bytes(data)
            if value > prev_value:
                count += 1
            prev_value = value

        if gap_in_data:
            fields.append(False)
            continue

        success = 1 < count >= incr_ratio * len(msgs)
        fields.append(success)
    return fields

def length(msgs, size, noise_ratio, num_iters, eps=1e-10):
    fields = []
    min_size = min(map(len, msgs))
    for i in range(0, min_size - size + 1, size):
        gap_in_data = False
        X = []
        for msg in msgs:
            data = msg[i:i+size]
            if 256 in data:
                gap_in_data = True
                break
            X.append(_get_value_from_bytes(data))

        if gap_in_data:
            fields.append(False)
            continue

        Y = [len(msg) for msg in msgs]
        XY = np.asarray([X, Y]).T

        try:
            (params, _, res) = ransac(XY, _model, 2, (1 - noise_ratio), num_iters, eps)
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

