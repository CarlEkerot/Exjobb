#! /usr/bin/env python

from __future__ import division

import util.ipv4_data
import sklearn
import sklearn.svm
import numpy as np

from annotator import Annotator

from features import *
from classifiers import *

# Define classifier and features
classifier = UDPClassifier
features = [
    PositionFeature(),
    DataFeature(),
    PredecessorFeature(),
    SuccessorFeature(),
]

# Extract messages
packets = util.ipv4_data.extract_pcap_data('../SkypeIRC.cap')['UDP']

# Annotate training and test data
annotator = Annotator(classifier, features)
(train_y, train_x) = annotator.annotate(packets[:500])
(test_y, test_x) = annotator.annotate(packets[500:1000])

# if we want use use class_weight we need to define it below
svc = sklearn.svm.LinearSVC()
params = {'C': range(1, 5)}
clf = sklearn.grid_search.GridSearchCV(svc, params)
# this had to be an ndarray to work
clf.fit(train_x, np.asarray(train_y))

pred_y = clf.predict(test_x)
conf = sklearn.metrics.confusion_matrix(test_y, pred_y)
print(clf.best_estimator_)
print(clf.score(test_x, test_y))
print(conf)
print('Field boundaries missed: %d (%.2f%%)' % (conf[0,1], 100 * conf[0,1] / (conf[0,1] + conf[1,1])))
print('False field boundaries: %d (%.2f%%)' % (conf[1,0], 100 * conf[1,0] / (conf[1,0] + conf[1,1])))
print(pred_y)

