from __future__ import division
import numpy
import re
import sklearn
import time

# from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
# from sklearn.multiclass import OneVsRestClassifier
# from sklearn.externals import joblib

# from collections import Counter
# from collections import defaultdict
# from cPickle import dump as pickle
# from Hierarchy import ROOT_BY_LEAF
# from Hierarchy import ROOT_BY_SOURCE
# from Tools import to_csv


class Classifier:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            input='content',
            min_df=1,
            use_idf=True
        )
        self.classifier = LogisticRegression(
            class_weight='balanced'
        )

    def train(self, tuples):
        start = time.time()
        if tuples:
            examples, labels, text_ids = zip(*tuples)
            matrix = self.vectorizer.fit_transform(examples)
            self.classifier.fit(
                matrix, labels
            )
            print 'took %.2f seconds to train' % (time.time() - start)
            return True
        return False

    def test(self, tuples, proba=True):
        start = time.time()
        examples, labels, text_ids = zip(*tuples)
        if examples:
            self.vectors = self.vectorizer.transform(examples)
            self.labels = labels
        if proba:
            predictions = self.classifier.predict_proba(self.vectors)
            predictions = [ sorted(zip(prediction, self.classifier.classes_), 
                                  reverse=True)
                           for prediction in predictions]
            return predictions
        else:
            return self.classifier.predict(self.vectors)


def f_score(accuracy, recall):
    return 2 * ((accuracy * recall) / (accuracy + recall))
