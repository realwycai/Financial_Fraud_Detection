# -*- coding: UTF-8 -*-
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor


def reduce_multicollinearity(data: pd.DataFrame) -> pd.DataFrame:
    idxs = []
    l = data.shape[1]
    VIF = [variance_inflation_factor(data.values, idx) for idx in range(l)]
    while max(VIF) > 100:
        idxs.append(np.argmax(VIF))
        VIF = [variance_inflation_factor(data.values, idx) for idx in range(l) if idx not in idxs]
    return data.iloc[:, [idx for idx in range(l) if idx not in idxs]]


def factors_match(all_factor: pd.DataFrame, violation_factor: pd.DataFrame) -> pd.DataFrame:
    all_factor_1 = all_factor.loc[(~all_factor.isna()).all(axis=1),]
    all_factor_final = industry_match(all_factor_1, violation_factor)
    data = pd.concat([all_factor_final, violation_factor], axis=0, ignore_index=True).drop('账面市值', axis=1)
    return data


def industry_match(all_factor: pd.DataFrame, violation_factor: pd.DataFrame) -> pd.DataFrame:
    all_factor_final = pd.DataFrame()
    violation_info = violation_factor[['violation_year', 'INDUSTRY_CSRC12_N']].drop_duplicates()
    print('各年份匹配行业的数量')
    for i in range(violation_info.shape[0]):
        tmp = all_factor.loc[(all_factor.violation_year == violation_info.iloc[i,]['violation_year']) &
                             (all_factor.INDUSTRY_CSRC12_N == violation_info.iloc[i,]['INDUSTRY_CSRC12_N']),]
        tmp = tmp.sort_values(by='账面市值', ascending=False).iloc[:10, ]
        all_factor_final = all_factor_final.append(tmp)
        print(violation_info.iloc[i,]['violation_year'], violation_info.iloc[i,]['INDUSTRY_CSRC12_N'], len(tmp))
    return all_factor_final

if __name__ == '__main__':
    all_factors = pd.read_excel('./data/全市场作为对照样本相应的数据/all_factors.xlsx')
    violation_factors = pd.read_excel('./data/全市场作为对照样本相应的数据/violation_factors.xlsx')
    factors_matched = factors_match(all_factors, violation_factors)
    factors_matched.to_excel('./data/全市场作为对照样本相应的数据/factors_matched.xlsx')