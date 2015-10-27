#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scikit-Learn Model-by-Cluster wrapper.

Original code by jnorthman: https://gist.github.com/jnothman/566ebde618ec18f2bea6
"""

import numpy as np

from sklearn.base import BaseEstimator, clone
from sklearn.utils import safe_mask


class ModelByCluster(BaseEstimator):
    """Cluster data, then run a regression independently on each cluster.

    Parameters
    ----------
    clusterer: scikit-learn style clustering model

    regression: scikit-learn style regression model
    """

    def __init__(self, clusterer, estimator):
        self.clusterer = clusterer
        self.estimator = estimator

    def fit(self, X, y):
        self.clusterer_ = clone(self.clusterer)
        clusters = self.clusterer_.fit_predict(X)
        n_clusters = len(np.unique(clusters))

        self.estimators_ = []
        for c in range(n_clusters):
            mask = clusters == c
            est = clone(self.estimator)
            est.fit(X[safe_mask(X, mask)], y[safe_mask(y, mask)])
            self.estimators_.append(est)
    
        return self

    def predict(self, X):
        clusters = self.clusterer_.predict(X)

        y_tmp = []
        idx = []
        for c, est in enumerate(self.estimators_):
            mask = clusters == c
            idx.append(np.flatnonzero(mask))
            y_tmp.append(est.predict(X[safe_mask(X, mask)]))

        y_tmp = np.concatenate(y_tmp)
        idx = np.concatenate(idx)
        y = np.empty_like(y_tmp)
        y[idx] = y_tmp

        return y
