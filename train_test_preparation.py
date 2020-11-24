# -*- coding: UTF-8 -*-
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import pandas as pd
import numpy as np
from statsmodels.stats.outliers_influence import variance_inflation_factor
from path import *

def avg_fill_na(data: pd.DataFrame):
    data1 = data.loc[:, ~data.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CITIC', '账面市值'])]
    data2 = data.loc[:, data.columns.isin(['Y', 'symbol', 'sheet_year', 'violation_year', 'INDUSTRY_CITIC', '账面市值'])]

    avg = data1.mean(axis=0, skipna=True)
    for column in data1.columns:
        data1[column].fillna(value=avg[column], inplace=True)
    for i in range(data1.shape[0]):
        for j in range(data1.shape[1]):
            try:
                if np.isinf(data1.iloc[i, j]):
                    data1.iloc[i, j] = avg[data1.columns[j]]
            except Exception:
                pass
    data3 = pd.concat([data1,data2], axis=1)
    return data3

def reduce_multicollinearity(data: pd.DataFrame) -> pd.DataFrame:
    columns_excluded = []
    reduced_data = data.copy(deep=True)
    VIF = {reduced_data.columns[idx]: variance_inflation_factor(reduced_data.values, idx) for idx in range(reduced_data.shape[1])}
    while max(VIF.values()) > 5:
        columns_max_vif = sorted(VIF.keys(), key= lambda x: VIF[x], reverse=True)[0]
        print(columns_max_vif)
        columns_excluded.append(columns_max_vif)
        reduced_data = reduced_data.loc[:, reduced_data.columns!=columns_max_vif]
        VIF =  {reduced_data.columns[idx]: variance_inflation_factor(reduced_data.values, idx) for idx in range(reduced_data.shape[1])}
    print(VIF)
    return reduced_data


def factors_match(all_factor: pd.DataFrame, violation_factor: pd.DataFrame) -> pd.DataFrame:
    all_factor_1 = all_factor.loc[(~all_factor.isna()).all(axis=1),]
    all_factor_final = industry_match(all_factor_1, violation_factor)
    data = pd.concat([all_factor_final, violation_factor], axis=0, ignore_index=True).drop('账面市值', axis=1)
    return data

# def industry_match(all_factor: pd.DataFrame, violation_factor: pd.DataFrame) -> pd.DataFrame:
#     CSI300_symbol_industry = pd.read_excel(data_path+'/CSI300_symbol_industry.xlsx')[['symbol', 'violation_year']].drop_duplicates()
#     CSI300_symbol_industry = CSI300_symbol_industry[CSI300_symbol_industry.violation_year>=2006]
#     return all_factor.merge(CSI300_symbol_industry, on=['symbol', 'violation_year'], how='inner')


def industry_match(all_factor: pd.DataFrame, violation_factor: pd.DataFrame) -> pd.DataFrame:
    all_factor_final = pd.DataFrame()
    # violation_info = violation_factor[['violation_year', 'INDUSTRY_CITIC']].drop_duplicates()
    violation_info = violation_factor[['violation_year', 'INDUSTRY_CITIC']].groupby(by=['violation_year', 'INDUSTRY_CITIC']).apply(lambda x: len(x)).reset_index(drop=False).rename(columns={0: 'num'})
    print('各年份匹配行业的数量')
    for i in range(violation_info.shape[0]):
        tmp = all_factor.loc[(all_factor.violation_year == violation_info.iloc[i,]['violation_year']) &
                             (all_factor.INDUSTRY_CITIC == violation_info.iloc[i,]['INDUSTRY_CITIC']),]
        tmp = tmp.sort_values(by='账面市值', ascending=False).iloc[:10*violation_info.iloc[i,]['num'], ]
        all_factor_final = all_factor_final.append(tmp)
        print(violation_info.iloc[i,]['violation_year'], violation_info.iloc[i,]['INDUSTRY_CITIC'], len(tmp))
    return all_factor_final

if __name__ == '__main__':
    all_factors = pd.read_excel(factors_path+'/all_factors.xlsx')
    violation_factors = pd.read_excel(factors_path+'/violation_factors.xlsx')
    all_factors = all_factors.loc[(~all_factors['symbol'].isin(violation_factors['symbol'].unique()))&(~all_factors['INDUSTRY_CITIC'].isin(['金融、保险业', '金融业'])),]
    factors_matched = factors_match(all_factors, violation_factors)
    factors_matched.to_excel(factors_path+'/factors_matched.xlsx')