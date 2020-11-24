# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""
from sklearn.metrics import *
import numpy as np


def metrics(actual, predict):
    print('confusion_matrix\n', confusion_matrix(actual, predict))

    print('accuracy_score', accuracy_score(actual, predict))

    print('precision_score', precision_score(actual, predict))

    print('recall_score', recall_score(actual, predict))

    print('roc_auc_score', roc_auc_score(actual, predict))


def metrices_opt(y_train, y_test, y_train_predict_prob, y_test_predict_prob, step: float = 0.02, start:float = 0.1, end:float = 1., thres:float = None):
    f1_res = {}
    if thres:
        thres_opt = thres
    else:
        thres_range = np.arange(start, end, step)
        for i in range(len(thres_range)):
            y_train_predict = (y_train_predict_prob > thres_range[i])
            f1 = np.round(f1_score(y_train, y_train_predict), 2)
            f1_res[i] = f1
        thres_opt = thres_range[sorted(f1_res.keys(), key = lambda x: f1_res[x], reverse=True)][0]
    y_train_predict = (y_train_predict_prob > thres_opt)
    y_test_predict = (y_test_predict_prob > thres_opt)
    print('Optimal thres is ', thres_opt)
    metrics(y_train, y_train_predict)
    metrics(y_test, y_test_predict)
    print('\n')
