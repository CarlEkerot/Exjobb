import scipy.sparse

class Annotator(object):
    def __init__(self, classifier, features):
        self.classifier = classifier
        self.features = features

    def annotate(self, msgs):
        num_bytes = 0
        num_features = 0
        for msg in msgs:
            num_bytes += len(msg)
        for feature in self.features:
            num_features += feature.size
        feature_matrix = scipy.sparse.lil_matrix((num_bytes, num_features), dtype=int)
        targets = []

        row = 0
        for msg in msgs:
            clf = self.classifier(msg)
            for pos in range(len(msg)):
                self._extract_features(msg, feature_matrix, row, pos)
                target = int(clf.is_boundary(pos))
                targets.append(target)
                row += 1
        return (targets, feature_matrix)

    def _extract_features(self, msg, feature_matrix, row, pos):
        count = 0
        for feature in self.features:
            val = feature.get_value(msg, pos)
            if feature.type_ == 'numeric':
                feature_matrix[row,count] = val
            elif feature.type_ == 'nominal':
                feature_matrix[row,count+val] = 1
            count += feature.size

