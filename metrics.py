# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""
from sklearn.metrics import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import platform
if platform.system() == 'Darwin':
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

def metrics(actual, predict):
    print('confusion_matrix\n', confusion_matrix(actual, predict))

    print('accuracy_score', accuracy_score(actual, predict))

    print('precision_score', precision_score(actual, predict))

    print('recall_score', recall_score(actual, predict))

def metrices_opt(y_train, y_test, y_train_predict_prob, y_test_predict_prob, step: float = 0.02, start:float = 0., end:float = 1., thres:float = None):
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

def __metrics_plot(thres_range, f1s, precisions, recalls, accuracys, roc, thres_opt, fpr, tpr, type):
    plt.close()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes = axes.flatten()
    # fig.tight_layout(pad=7.)
    fig.suptitle(f'{type} 预测效果vs判断阈值, roc_auc_score={roc}', fontsize=20)
    axes[0].plot(thres_range, [np.round(x,2)*100 for x in precisions], label='Precision', linewidth='2')
    axes[0].plot(thres_range, [np.round(x,2)*100 for x in recalls], label='Recall', linewidth='2')
    axes[0].axvline(x=thres_opt, ymin=0, ymax=1, linewidth='2', color='red', linestyle='--')
    axes[0].text(thres_opt + 0.05, 0.8, "F1最大", fontsize=10)
    axes[0].set_ylim(0, 120)
    axes[0].set_ylabel("%", fontsize=10)
    axes[0].set_xlabel("阈值", fontsize=10)
    axes[0].legend(fontsize=10)
    axes[1].plot(thres_range, [np.round(x,2)*100 for x in f1s], label='F1 Score', linewidth='2')
    axes[1].plot(thres_range, [np.round(x,2)*100 for x in accuracys], label='Accuracy', linewidth='2')
    axes[1].axvline(x=thres_opt, ymin=0, ymax=1, linewidth='2', color='red', linestyle='--')
    axes[1].text(thres_opt + 0.05, 0.8, "F1最大", fontsize=10)
    axes[1].set_ylim(0, 120)
    axes[1].set_ylabel("%", fontsize=10)
    axes[1].set_xlabel("阈值", fontsize=10)
    axes[1].legend(fontsize=10)
    axes[2].plot([np.round(x,2)*100 for x in fpr], [np.round(x,2)*100 for x in tpr], label='ROC', linewidth='2')
    axes[2].set_xlabel("False Positive Rate %", fontsize=10)
    axes[2].set_ylabel("True Positive Rate % = Recall %", fontsize=10)
    axes[2].legend(fontsize=10)
    plt.show()

def metrics_plot(y_train, y_test, y_train_predict_prob, y_test_predict_prob, step: float = 0.02, start:float = 0., end:float = 1.):
    thres_range = np.arange(start, end, step)
    f1s = []
    precisions = []
    recalls = []
    accuracys = []
    for i in range(len(thres_range)):
        y_train_predict = (y_train_predict_prob > thres_range[i])
        f1s.append(f1_score(y_train, y_train_predict))
        precision = precision_score(y_train, y_train_predict)
        if not precision:
            precisions.append(np.nan)
        else:
            precisions.append(precision)
        recall = recall_score(y_train, y_train_predict)
        if not recall:
            recalls.append(np.nan)
        else:
            recalls.append(recall)
        accuracys.append(accuracy_score(y_train, y_train_predict))
    roc = roc_auc_score(y_train, y_train_predict_prob)
    fpr, tpr, thresholds = roc_curve(y_train, y_train_predict_prob)
    opt_idx = np.argmax(f1s)
    thres_opt = start + opt_idx*step
    __metrics_plot(thres_range, f1s, precisions, recalls, accuracys, roc, thres_opt, fpr, tpr, '训练集')


    f1s = []
    precisions = []
    recalls = []
    accuracys = []
    for i in range(len(thres_range)):
        y_test_predict = (y_test_predict_prob > thres_range[i])
        f1s.append(f1_score(y_test, y_test_predict))
        precision = precision_score(y_test, y_test_predict)
        if not precision:
            precisions.append(np.nan)
        else:
            precisions.append(precision)
        recall = recall_score(y_test, y_test_predict)
        if not recall:
            recalls.append(np.nan)
        else:
            recalls.append(recall)
        accuracys.append(accuracy_score(y_test, y_test_predict))
    roc = roc_auc_score(y_test, y_test_predict_prob)
    fpr, tpr, thresholds = roc_curve(y_test, y_test_predict_prob)
    __metrics_plot(thres_range, f1s, precisions, recalls, accuracys, roc, thres_opt, fpr, tpr, '测试集')