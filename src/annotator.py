import scipy.sparse

def annotate(msgs, classifier, features):
    num_bytes = 0
    num_features = 0
    for msg in msgs:
        num_bytes += len(msg)
    for feature in features:
        num_features += feature.size
    feature_matrix = scipy.sparse.lil_matrix((num_bytes, num_features), dtype=int)
    targets = []

    row = 0
    for msg in msgs:
        classifier.init(msg)
        for pos in range(len(msg)):
            _extract_features(msg, features, feature_matrix, row, pos)
            target = int(classifier.is_boundary(pos))
            targets.append(target)
            row += 1
    return (targets, feature_matrix)

def _extract_features(msg, features, feature_matrix, row, pos):
    count = 0
    for feature in features:
        val = feature.get_value(msg, pos)
        if feature.type_ == 'numeric':
            feature_matrix[row,count] = val
        elif feature.type_ == 'nominal':
            feature_matrix[row,count+val] = 1
        count += feature.size

