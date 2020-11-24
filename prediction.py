# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd

from metrics import *
from path import *

if __name__ == '__main__':
    data = pd.read_excel(factors_path+'/factors_matched.xlsx')
    X_train = data.loc[(data.violation_year >= 2007)&(data.violation_year <= 2015), ~data.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CSRC12_N'])]
    # X_train = reduce_multicollinearity(X_train)
    X_test = data.loc[data.violation_year >= 2016, ~data.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CSRC12_N'])]
    y_train = data.loc[(data.violation_year >= 2007)&(data.violation_year <= 2015), 'Y']
    y_test = data.loc[data.violation_year >= 2016, 'Y']

    smo = SMOTE(sampling_strategy = {1: 260}, random_state=20, n_jobs = -1)
    X_train, y_train = smo.fit_resample(X_train, y_train)

    # rus = RandomUnderSampler(sampling_strategy={0: 1000}, random_state=20, replacement=False)
    # X_train, y_train = rus.fit_resample(X_train, y_train)

    # X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.4, random_state=0)
    # X_train, y_train = X_resampled, y_resampled
    lr = LogisticRegression(penalty='none', solver='newton-cg', max_iter=10000, n_jobs=-1)
    lr.fit(X_train, y_train)
    print('LR')
    # metrics(y_train, lr.predict(X_train))
    # metrics(y_test, lr.predict(X_test))
    y_train_predict_prob = lr.predict_proba(X_train)[:, 1]
    y_test_predict_prob = lr.predict_proba(X_test)[:, 1]
    metrics_plot(y_train, y_test, y_train_predict_prob, y_test_predict_prob)

    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    print('Rf')
    # metrics(y_train, rf.predict(X_train))
    # metrics(y_test, rf.predict(X_test))
    y_train_predict_prob = rf.predict_proba(X_train)[:, 1]
    y_test_predict_prob = rf.predict_proba(X_test)[:, 1]
    metrics_plot(y_train, y_test, y_train_predict_prob, y_test_predict_prob)
