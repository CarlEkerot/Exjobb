import numpy
import collections
import sklearn.cluster
import scipy.spatial.distance as dist

def cluster(msgs, size, eps, min_samples, filter_func=lambda x: 1, limit=100):
    # Limit number of messages and the size of each message
    msgs = map(lambda x: x.data[:limit], msgs[:size])

    # Calculate probability matrix for the different byte values
    P = numpy.zeros((limit, 256))
    for msg in msgs:
        for (pos, val) in enumerate(msg):
            P[pos,ord(val)] += 1
    P = P / len(msgs)

    samples = []
    for (i, msg) in enumerate(msgs):
        features = numpy.zeros(limit)
        for (j, byte) in enumerate(msg):
            features[j] = filter_func(j) * P[j,ord(byte)]
        samples.append(features)

    # Create distance matrix
    dist_matrix = dist.squareform(dist.pdist(samples))

    # Normalize distances
    norm_dists = dist_matrix / numpy.max(dist_matrix)

    # Perform clustering
    seed = 0
    state = numpy.random.RandomState(seed)
    prediction = sklearn.cluster.DBSCAN(eps=eps, min_samples=min_samples,
            metric='precomputed', random_state=state).fit_predict(norm_dists)

    result = collections.defaultdict(list)
    for i, label in enumerate(prediction):
        result[label].append(i)

    return result

