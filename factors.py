# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import os
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count

from path import *

def current_period_factor_calculation(bs_data: pd.DataFrame, is_data: pd.DataFrame, cs_data: pd.DataFrame, other_data: pd.DataFrame) -> pd.DataFrame:
    return_data = pd.DataFrame()
    bs_data = bs_data.copy(deep=True)
    is_data = is_data.copy(deep=True)
    cs_data = cs_data.copy(deep=True)
    other_data = other_data.copy(deep=True)

    bs_data['INVENTORIES'].fillna(value=0, inplace=True)
    bs_data['ACCT_RCV'].fillna(value=0, inplace=True)  # 应收账款可能为0
    bs_data['OTH_RCV_TOT'].fillna(value=0, inplace=True)  # 其他应收款可能为0
    bs_data['STMNOTE_ASSETDETAIL_2'].fillna(value=0, inplace=True) # 折旧和摊销可能为0
    bs_data['STMNOTE_ASSETDETAIL_1'].fillna(value=0, inplace=True)
    bs_data['NON_CUR_LIAB_DUE_WITHIN_1Y'].fillna(value=0, inplace=True)
    bs_data['TAXES_SURCHARGES_PAYABLE'].fillna(value=0, inplace=True)
    is_data['FIN_EXP_IS'].fillna(value=0, inplace=True)
    bs_data['TOT_NON_CUR_LIAB'].fillna(value=0, inplace=True) # 长期负债可能为0
    bs_data['DVD_PAYABLE'].fillna(value=0, inplace=True) # 应发股利可能为0
    # other_data['股票月换手率波动率'].fillna(value=0, inplace=True)
    # other_data['H5指数'].fillna(value=0, inplace=True)
    # other_data['机构投资者持股比例'].fillna(value=0, inplace=True)
    other_data['是否再融资'].fillna(value=0, inplace=True)
    other_data['关联交易金额'].fillna(value=0, inplace=True)
    # other_data['监事会人数'].fillna(value=0, inplace=True)
    # other_data['Z指数'].fillna(value=0, inplace=True)
    # other_data['是否非标准审计意见'].fillna(value=0, inplace=True)
    other_data['国有股比例'].fillna(value=0, inplace=True)

    static_data = bs_data.iloc[1:,].loc[:, ['symbol', 'sheet_year', 'violation_year']].copy(deep=True)
    """
    偿债能力指标：
    1. 流动比率=流动资产/流动负债
    2. 速动比率=（流动资产-存货）/流动负债
    3. 利息保障倍数=(利润总额+利息费用)/利息费用
    4. 资产负债率=总负债/总资产
    5. 负债保障倍数=经营活动产生的现金流量净额/平均总负债
    """
    static_data['流动比率'] = bs_data.iloc[1:,]['TOT_CUR_ASSETS'].values / bs_data.iloc[1:,]['TOT_CUR_LIAB'].values
    static_data['速动比率'] = (bs_data.iloc[1:,]['TOT_CUR_ASSETS'].values-bs_data.iloc[1:,]['INVENTORIES'].values) / bs_data.iloc[1:,]['TOT_CUR_LIAB'].values
    static_data['利息保障倍数'] = (is_data.iloc[1:,]['TOT_PROFIT'].values + is_data.iloc[1:,]['FIN_EXP_IS'].values) / is_data.iloc[1:,]['FIN_EXP_IS'].values
    static_data['资产负债率'] = bs_data.iloc[1:,]['TOT_LIAB'].values / bs_data.iloc[1:,]['TOT_ASSETS'].values
    static_data['负债保障倍数'] = cs_data.iloc[1:,]['NET_CASH_FLOWS_OPER_ACT'].values / ((bs_data.iloc[1:,]['TOT_LIAB'].values + bs_data.iloc[:-1,]['TOT_LIAB'].values)/2)
    """
    经营能力指标：
    6. 应收账款比率=平均应收账款/总收入
    7. 应收账款占比=应收账款/总资产
    8. 存货周转率倒数=平均存货余额/营业成本
    9. 总资产周转率=销售收入净额/平均资产总额
    10. 其他应收款比率 = 其他应收款/总资产
    11. 折旧率=折旧费用/固定资产原值=（固定资产累计折旧年末-年初）/固定资产账面原值
    12. 总应计项=应计项/总资产，应计项=（流动资产变化-货币资金变化）-（流动负债变化 - 一年内到期长期负债变化-应交税费变化）- 折旧费用
    13. 现金销售率=（营业收入-应收账款变化）/营业收入
    14. 是否亏损 = 净利润
    """
    static_data['应收账款比率'] = ((bs_data.iloc[1:,]['ACCT_RCV'].values + bs_data.iloc[:-1,]['ACCT_RCV'].values)/2) / is_data.iloc[1:,]['TOT_OPER_REV'].values
    static_data['应收账款占比'] = bs_data.iloc[1:,]['ACCT_RCV'].values / bs_data.iloc[1:,]['TOT_ASSETS'].values
    static_data['存货周转率倒数'] =  ((bs_data.iloc[1:,]['INVENTORIES'].values + bs_data.iloc[:-1,]['INVENTORIES'].values)/2) / is_data.iloc[1:,]['OPER_COST'].values
    static_data['总资产周转率'] =  is_data.iloc[1:,]['TOT_OPER_REV'].values / ((bs_data.iloc[1:,]['TOT_ASSETS'].values + bs_data.iloc[:-1,]['TOT_ASSETS'].values)/2)
    static_data['其他应收款比率'] = bs_data.iloc[1:,]['OTH_RCV_TOT'].values / bs_data.iloc[1:,]['TOT_ASSETS'].values
    static_data['折旧率'] = (bs_data.iloc[1:,]['STMNOTE_ASSETDETAIL_2'].values - bs_data.iloc[:-1,]['STMNOTE_ASSETDETAIL_2'].values)/ bs_data.iloc[1:,]['STMNOTE_ASSETDETAIL_1'].values
    static_data['折旧率'].fillna(value=0, inplace=True)
    static_data['总应计项'] = (((bs_data.iloc[1:,]['TOT_CUR_ASSETS'].values - bs_data.iloc[:-1,]['TOT_CUR_ASSETS'].values)
           - (bs_data.iloc[1:,]['MONETARY_CAP'].values - bs_data.iloc[:-1,]['MONETARY_CAP'].values)) -
          ((bs_data.iloc[1:,]['TOT_CUR_LIAB'].values - bs_data.iloc[:-1,]['TOT_CUR_LIAB'].values)
           - (bs_data.iloc[1:,]['NON_CUR_LIAB_DUE_WITHIN_1Y'].values- bs_data.iloc[:-1,]['NON_CUR_LIAB_DUE_WITHIN_1Y'].values)
           - (bs_data.iloc[1:,]['TAXES_SURCHARGES_PAYABLE'].values - bs_data.iloc[:-1,]['TAXES_SURCHARGES_PAYABLE'].values)) -
          (bs_data.iloc[1:,]['STMNOTE_ASSETDETAIL_2'].values - bs_data.iloc[:-1,]['STMNOTE_ASSETDETAIL_2'].values)) / \
                         bs_data.iloc[1:,]['TOT_ASSETS'].values
    static_data['现金销售率'] = (is_data.iloc[1:,]['TOT_OPER_REV'].values - (bs_data.iloc[1:,]['ACCT_RCV'].values - bs_data.iloc[:-1,]['ACCT_RCV'].values)) /is_data.iloc[1:,]['TOT_OPER_REV'].values
    """
    盈利能力指标：
    15. 资产报酬率=(净利润+利息费用+所得税)/平均资产总额 = (利润总额+利息费用)/平均资产总额
    16. 总资产收益率=净利润/平均资产总额
    17. 净资产收益率=净利润/平均净资产总额
    18. 长期资本报酬率=(净利润+利息费用+所得税)/（长期负债平均值+所有者权益平均值）
    19. 营业毛利率=(主营业务收入-主营业务成本)/主营业务收入
    """
    static_data['资产报酬率'] = (is_data.iloc[1:,]['TOT_PROFIT'].values + is_data.iloc[1:,]['FIN_EXP_IS'].values) / ((bs_data.iloc[1:,]['TOT_ASSETS'].values + bs_data.iloc[:-1,]['TOT_ASSETS'].values)/2)
    static_data['总资产收益率'] =  is_data.iloc[1:,]['NET_PROFIT_IS'].values / ((bs_data.iloc[1:,]['TOT_ASSETS'].values + bs_data.iloc[:-1,]['TOT_ASSETS'].values)/2)
    static_data['净资产收益率'] =  is_data.iloc[1:,]['NET_PROFIT_IS'].values / ((bs_data.iloc[1:,]['TOT_EQUITY'].values + bs_data.iloc[:-1,]['TOT_EQUITY'].values)/2)
    static_data['长期资本报酬率'] =  (is_data.iloc[1:,]['TOT_PROFIT'].values + is_data.iloc[1:,]['FIN_EXP_IS'].values) / ((bs_data.iloc[1:,]['TOT_NON_CUR_LIAB'].values + bs_data.iloc[1:,]['TOT_EQUITY'].values + bs_data.iloc[:-1,]['TOT_NON_CUR_LIAB'].values + bs_data.iloc[:-1,]['TOT_EQUITY'].values)/2)
    static_data['营业毛利率'] = (is_data.iloc[1:,]['OPER_REV'].values) / is_data.iloc[1:,]['OPER_COST'].values - 1
    """
    发展能力指标：
    20. 资产保值增值率=期末所有者权益/期初所有者权益-1
    21. 总资产增值率=期末总资产/期初总资产-1
    22. 利润总额增长率=本期利润总额/上期利润总额-1
    23. 利润存留率=（税后利润-应发股利）/税后利润
    24. 可持续增长率=净资产收益率*利润留存率/（1-净资产收益率*利润留存率）
    """
    static_data['资产保值增值率'] = bs_data.iloc[1:,]['TOT_EQUITY'].values / bs_data.iloc[:-1,]['TOT_EQUITY'].values - 1
    static_data['总资产增值率'] =  bs_data.iloc[1:,]['TOT_ASSETS'].values / bs_data.iloc[:-1,]['TOT_ASSETS'].values - 1
    static_data['利润总额增长率'] = is_data.iloc[1:,]['TOT_PROFIT'].values / is_data.iloc[:-1,]['TOT_PROFIT'].values - 1
    static_data['利润存留率'] = (is_data.iloc[1:,]['NET_PROFIT_IS'].values - (bs_data.iloc[1:,]['DVD_PAYABLE'].values + bs_data.iloc[:-1,]['DVD_PAYABLE'].values) / 2)/ is_data.iloc[1:,]['NET_PROFIT_IS'].values
    static_data['可持续增长率'] = static_data['净资产收益率'].values * static_data['利润存留率'].values / (1 - static_data['净资产收益率'].values * static_data['利润存留率'].values)

    """
    计算各个数量化指标的变化率
    """
    dynamic_data_tmp = static_data.loc[:, ~static_data.columns.isin(['symbol', 'sheet_year', 'violation_year'])].copy(deep=True)
    dynamic_data = dynamic_data_tmp.iloc[1,] / dynamic_data_tmp.iloc[0,] - 1
    dynamic_data = dynamic_data.rename(index={x: x + '_grow_rate' for x in dynamic_data.index})
    for index in dynamic_data.index:
        if np.isinf(dynamic_data[index]) or pd.isna(dynamic_data[index]):
            dynamic_data[index] = 0
    """
    其他指标：
    25. 
    """
    static_data['今年是否亏损'] = is_data.iloc[1:,]['NET_PROFIT_IS'].apply(lambda x: 1 if x<0 else 0).values
    static_data['去年是否亏损'] = is_data.iloc[:-1,]['NET_PROFIT_IS'].apply(lambda x: 1 if x<0 else 0).values

    static_data['股票月换手率波动率'] = other_data.iloc[1:, ]['股票月换手率波动率'].values
    static_data['H5指数'] = other_data.iloc[1:, ]['H5指数'].values
    static_data['机构投资者持股比例'] = other_data.iloc[1:, ]['机构投资者持股比例'].values
    static_data['是否再融资'] = other_data.iloc[1:, ]['是否再融资'].values
    static_data['股市周期'] = other_data.iloc[1:, ]['等权平均市场年收益率'].apply(lambda x: 1 if x<0 else 0).values
    static_data['关联交易影响度'] = other_data.iloc[1:, ]['关联交易金额'].values/bs_data.iloc[1:,]['TOT_ASSETS'].values
    static_data['关联交易影响度'] = other_data.iloc[1:, ]['关联交易金额'].values/bs_data.iloc[1:,]['TOT_ASSETS'].values
    if (not pd.isna(other_data.iloc[1:, ]['董事长'].values).any()) and other_data.iloc[1, ]['董事长'] != other_data.iloc[2, ]['董事长']:
        static_data['董事长是否变更'] = np.array([0, 1])
    else:
        static_data['董事长是否变更'] = np.array([0, 0])
    static_data['监事会规模'] = other_data['监事会人数'].mean(skipna=True)
    static_data['Z指数'] = other_data.iloc[1:, ]['Z指数'].values
    static_data['是否非标准审计意见'] = other_data.iloc[1:, ]['是否非标准审计意见'].values
    if (not pd.isna(other_data.iloc[1:, ]['会计师事务所'].values).any()) and other_data.iloc[1, ]['会计师事务所'] != other_data.iloc[2, ]['会计师事务所']:
        static_data['会计师事务所是否变更'] = np.array([0, 1])
    else:
        static_data['会计师事务所是否变更'] = np.array([0, 0])
    static_data['国有股比例'] = other_data.iloc[1:, ]['国有股比例'].values

    # for j in range(static_data.shape[1]):
    #     try:
    #         if np.isinf(static_data.iloc[1, j]):
    #             static_data.iloc[1, j] = 0
    #     except Exception:
    #         pass

    return_data = static_data.iloc[1,].append(dynamic_data)
    return_data['账面市值'] = bs_data.iloc[-1,]['TOT_ASSETS']
    return_data['INDUSTRY_CITIC'] = bs_data.iloc[-1,]['INDUSTRY_CITIC']
    return return_data

def factors_preparation():
    os.chdir(data_path)
    violation_bs = pd.read_excel('violation_bs.xlsx')
    violation_bs = violation_bs.sort_values(by=['symbol','sheet_year']).groupby(by=['symbol', 'violation_year'])
    violation_is = pd.read_excel('violation_is.xlsx')
    violation_is = violation_is.sort_values(by=['symbol', 'sheet_year']).groupby(by=['symbol', 'violation_year'])
    violation_cs = pd.read_excel('violation_cs.xlsx')
    violation_cs = violation_cs.sort_values(by=['symbol','sheet_year']).groupby(by=['symbol', 'violation_year'])
    violation_other = pd.read_excel('violation_other.xlsx')
    violation_other = violation_other.sort_values(by=['symbol', 'sheet_year']).groupby(by=['symbol', 'violation_year'])

    all_industry = pd.read_excel('stock_all_symbol_industry.xlsx')
    all_bs = pd.read_excel('all_bs.xlsx')
    all_bs = all_bs.merge(all_industry, how='left', on=['symbol', 'sheet_year'])
    all_bs = all_bs.sort_values(by=['symbol','sheet_year']).groupby(by=['symbol', 'violation_year'])
    all_is = pd.read_excel('all_is.xlsx')
    all_is = all_is.merge(all_industry, how='left', on=['symbol', 'sheet_year'])
    all_is = all_is.sort_values(by=['symbol','sheet_year']).groupby(by=['symbol', 'violation_year'])
    all_cs = pd.read_excel('all_cs.xlsx')
    all_cs = all_cs.merge(all_industry, how='left', on=['symbol', 'sheet_year'])
    all_cs = all_cs.sort_values(by=['symbol','sheet_year']).groupby(by=['symbol', 'violation_year'])
    all_other = pd.read_excel('all_other.xlsx')
    all_other = all_other.sort_values(by=['symbol', 'sheet_year']).groupby(by=['symbol', 'violation_year'])

    cpu_nums = cpu_count()
    p = Pool(cpu_nums)
    pools = []
    for symbol in violation_bs.groups:
        pools.append(p.apply_async(current_period_factor_calculation, args=(violation_bs.get_group(symbol), violation_is.get_group(symbol), violation_cs.get_group(symbol), violation_other.get_group(symbol),)))
    p.close()
    p.join()
    violation_factor = pd.DataFrame()
    for pool in pools:
        violation_factor = violation_factor.append(pool.get(), ignore_index=True)

    p = Pool(cpu_nums)
    pools = []
    for symbol in all_bs.groups:
        if symbol not in all_other.groups:
            continue
        pools.append(p.apply_async(current_period_factor_calculation, args=(all_bs.get_group(symbol), all_is.get_group(symbol), all_cs.get_group(symbol), all_other.get_group(symbol),)))
    p.close()
    p.join()
    all_factor = pd.DataFrame()
    for pool in pools:
        all_factor = all_factor.append(pool.get(), ignore_index=True)

    violation_factor['Y'] = 1
    all_factor['Y'] = 0

    return violation_factor, all_factor

if __name__ == '__main__':
    violation_factors, all_factors = factors_preparation()
    violation_factors.to_excel(factors_path + '/violation_factors.xlsx', index=False)
    all_factors.to_excel(factors_path + '/all_factors.xlsx', index=False)