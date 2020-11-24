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

from train_test_preparation import *
from metrics import *
from path import *

if __name__ == '__main__':
    all_factors = pd.read_excel(factors_path + '/all_factors.xlsx')
    violation_factors = pd.read_excel(factors_path + '/violation_factors.xlsx')
    # all_factors = all_factors[~all_factors.isna().any(axis=1)]
    all_factors = all_factors.loc[~all_factors['INDUSTRY_CITIC'].isin(['银行', '非银行金融', '综合金融']),]
    all_factors = all_factors.loc[~all_factors['INDUSTRY_CITIC'].isna(),]

    # all_factors_1 = all_factors.loc[:, ~all_factors.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CITIC', '账面市值'])]
    # all_factors_1 = reduce_multicollinearity(all_factors_1)
    # all_factors_2 = all_factors.loc[:, all_factors.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CITIC', '账面市值'])]
    # all_factors = pd.concat([all_factors_1,all_factors_2], axis=1)
    # all_factors = all_factors.loc[~all_factors['symbol'].isin(violation_factors['symbol'].unique()),]

    all_factors_train = all_factors.loc[(all_factors.violation_year >= 2006)&(all_factors.violation_year <= 2015),]
    violation_factors_train = violation_factors.loc[(violation_factors.violation_year >= 2006)&(violation_factors.violation_year <= 2015), violation_factors.columns.isin(all_factors.columns)]
    all_factors_train_matched = factors_match(all_factors_train, violation_factors_train)
    # all_factors_train_matched = all_factors_train
    train_data = pd.concat([all_factors_train_matched, violation_factors_train], axis=0).reset_index(drop=True)
    train_data = train_data.groupby(by=['violation_year', 'INDUSTRY_CITIC']).apply(avg_fill_na).reset_index(drop=True)
    X_train = train_data.loc[:, ~train_data.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CITIC', '账面市值'])]
    X_train = reduce_multicollinearity(X_train)
    y_train = train_data.loc[:, 'Y']

    all_factors_test = all_factors.loc[(all_factors.violation_year > 2015),]
    violation_factors_test = violation_factors.loc[(violation_factors.violation_year > 2015), violation_factors.columns.isin(all_factors.columns)]
    test_data = pd.concat([all_factors_test, violation_factors_test], axis=0).reset_index(drop=True)
    test_data = test_data.groupby(by=['violation_year', 'INDUSTRY_CITIC']).apply(avg_fill_na).reset_index(drop=True)
    X_test = test_data.loc[:, test_data.columns.isin(X_train.columns)]
    y_test = test_data.loc[:, 'Y']

    # smo = SMOTE(sampling_strategy = {1: 500}, random_state=20, n_jobs = -1)
    # X_train, y_train = smo.fit_resample(X_train, y_train)

    # rus = RandomUnderSampler(sampling_strategy={0: 1000}, random_state=20, replacement=False)
    # X_train, y_train = rus.fit_resample(X_train, y_train)

    # X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.4, random_state=0)
    # X_train, y_train = X_resampled, y_resampled
    rf = RandomForestClassifier(class_weight='balanced')
    rf.fit(X_train, y_train)
    print('Rf')
    y_train_predict_prob = rf.predict_proba(X_train)[:, 1]
    y_test_predict_prob = rf.predict_proba(X_test)[:, 1]
    metrices_opt(y_train, y_test, y_train_predict_prob, y_test_predict_prob)
    metrics_plot(y_train, y_test, y_train_predict_prob, y_test_predict_prob)

    lr = LogisticRegression(C=0.01, penalty='l1', solver='liblinear', max_iter=10000, n_jobs=-1, class_weight='balanced')
    lr.fit(X_train, y_train)
    print('LR')
    y_train_predict_prob = lr.predict_proba(X_train)[:, 1]
    y_test_predict_prob = lr.predict_proba(X_test)[:, 1]
    metrices_opt(y_train, y_test, y_train_predict_prob, y_test_predict_prob)
    metrics_plot(y_train, y_test, y_train_predict_prob, y_test_predict_prob)