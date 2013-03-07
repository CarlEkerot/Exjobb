#! /usr/bin/env python

from __future__ import division

import util.ipv4_data
import pcap_reassembler
import sklearn
import sklearn.svm
import sklearn.metrics
import numpy as np
import scipy.sparse as sp

from sklearn.externals import joblib
import os

from annotator import Annotator

from features import *
from classifiers import *

import warnings

warnings.simplefilter('ignore', DeprecationWarning)

# Define features
features = [
    PositionFeature(),
    DataFeature(),
    PredecessorFeature(),
    SuccessorFeature(),
    ByteDifferenceFeature(),
    ByteXORFeature(),
]

# Define annotators
dns_anot = Annotator(DNSClassifier, features)

# Extract messages
dns_packets = pcap_reassembler.load_pcap('../dns-30628-packets.pcap')

if os.path.exists('model/model'):
    # Load the model
    print("loading model from file")
    clf = joblib.load('model/model')
else:
    print("creating new model")

    # Annotate training data
    (train_y, train_x) = dns_anot.annotate(map(lambda x: x.data, dns_packets[0:6000]))

    # Train the model
    svc = sklearn.svm.LinearSVC(dual=False, class_weight='auto')
    params = {'C': range(1,11)}
    clf = sklearn.grid_search.GridSearchCV(svc, params)
    clf.fit(train_x, np.asarray(train_y))
    print('Best estimator:')
    print(clf.best_estimator_)

    # Save the model
    joblib.dump(clf.best_estimator_, 'model/model')

# Test the model
dns_packets = pcap_reassembler.load_pcap('../dns-30628-packets.pcap')
(test_y, test_x) = dns_anot.annotate(map(lambda x: x.data, dns_packets[6000:7000]))
pred_y = clf.predict(test_x)

# Output prediction information
score = sklearn.metrics.accuracy_score(test_y, pred_y)
score_zeros = sklearn.metrics.accuracy_score(test_y, len(pred_y) * [0])
C = sklearn.metrics.confusion_matrix(test_y, pred_y)
print('Accuracy score: %.2f%%' % (100 * score))
print('Zero-prediction comparison: %.2f%%' % (100 * score / score_zeros))
print('Confusion matrix:')
print(C)
print('Field boundaries missed (false negatives): %d (%.2f%%)' % (C[1,0], 100 * C[1,0] / (C[1,0] + C[1,1])))
print('False field boundaries (false positives): %d (%.2f%%)' % (C[0,1], 100 * C[0,1] / (C[0,1] + C[1,1])))
print('Prediction:')
print(pred_y)

