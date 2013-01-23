#! /usr/bin/env python

import util.ipv4_data
import sklearn
import sklearn.svm
import numpy as np

from annotator import annotate

from features import *
from classifiers import *

# Define classifier and features
classifier = UDPClassifier()
features = [
    PositionFeature(),
    DataFeature(),
    PredecessorFeature(),
    SuccessorFeature(),
]

# Extract messages
packets = util.ipv4_data.extract_pcap_data('../SkypeIRC.cap')['UDP']

# Annotate training and test data
(train_y, train_x) = annotate(packets[:500], classifier, features)
(test_y, test_x) = annotate(packets[500:1000], classifier, features)

# if we want use use class_weight we need to define it below
svc = sklearn.svm.LinearSVC()
params = {'C': range(1, 5)}
clf = sklearn.grid_search.GridSearchCV(svc, params)
# this had to be an ndarray to work
clf.fit(train_x, np.asarray(train_y))

print(clf.best_estimator_)
print(clf.score(test_x, test_y))
pred_y = clf.predict(test_x)
print(sklearn.metrics.confusion_matrix(test_y, pred_y))
print(pred_y)

