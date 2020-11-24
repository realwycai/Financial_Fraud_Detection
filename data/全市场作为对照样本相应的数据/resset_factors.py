# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import os
import pandas as pd
import numpy as np

from path import *

def bs_check():
    m = 0
    for i in range(bs_violation.shape[0]):
        resset_data = bs_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        # if (symbol, sheet_year) in [('000504.SZ', 2012),
        #                             ('000519.SZ', 2014),
        #                             ('000519.SZ', 2015),]:
        #     continue
        wind_data = violation_bs.loc[(violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['货币资金(元)_CashEqv'] - wind_data['MONETARY_CAP'] == 0
            assert resset_data['应收账款(元)_AccRec'] - wind_data['ACCT_RCV'] == 0
            if not pd.isna(resset_data['其他应收款(元)_OthRec']):
                assert resset_data['其他应收款(元)_OthRec'] - wind_data['OTH_RCV_TOT'] == 0
            if not pd.isna(resset_data['存货(元)_Inventories']):
                assert resset_data['存货(元)_Inventories'] - wind_data['INVENTORIES'] == 0
            assert resset_data['流动资产合计(元)_TotCurrAss'] - wind_data['TOT_CUR_ASSETS'] == 0
            assert resset_data['资产总计(元)_TotAss'] - wind_data['TOT_ASSETS'] == 0
            if not pd.isna(resset_data['应付股利(元)_DividPay']):
                assert resset_data['应付股利(元)_DividPay'] - wind_data['DVD_PAYABLE'] == 0
            if not pd.isna(resset_data['应交税费(元)_TaxPay']):
                assert resset_data['应交税费(元)_TaxPay'] - wind_data['TAXES_SURCHARGES_PAYABLE'] == 0
            if not pd.isna(resset_data['一年内到期的非流动负债(元)_NCurrLiabOne']):
                assert resset_data['一年内到期的非流动负债(元)_NCurrLiabOne'] - wind_data['NON_CUR_LIAB_DUE_WITHIN_1Y'] == 0
            assert resset_data['流动负债合计(元)_TotCurLia'] - wind_data['TOT_CUR_LIAB'] == 0
            # assert resset_data['非流动负债合计(元)_TotNCurLia'] - wind_data['TOT_NON_CUR_LIAB'] == 0
            assert resset_data['负债合计(元)_TotLiab'] - wind_data['TOT_LIAB'] == 0
            assert resset_data['所有者权益（或股东权益）合计(元)_TotShareEquit'] - wind_data['TOT_EQUITY'] == 0
        except AssertionError:
            m = m + 1


def is_check():
    m = 0
    for i in range(is_violation.shape[0]):
        resset_data = is_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        # if (symbol, sheet_year) in [('000504.SZ', 2012),
        #                             ('000519.SZ', 2014),
        #                             ('000519.SZ', 2015),]:
        #     continue
        wind_data = violation_is.loc[(violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['利润总额()_TotProf'] - wind_data['TOT_PROFIT'] == 0
            assert resset_data['财务费用()_FinanExp'] - wind_data['FIN_EXP_IS'] == 0
            assert resset_data['营业成本()_OpCost'] - wind_data['OPER_COST'] == 0
            assert resset_data['营业总收入()_TotOpRev'] - wind_data['TOT_OPER_REV'] == 0
            assert resset_data['净利润()_NetProf'] - wind_data['NET_PROFIT_IS'] == 0
            assert resset_data['营业收入()_OpRev'] - wind_data['OPER_REV'] == 0
        except AssertionError:
            m = m + 1


def cs_check():
    m = 0
    for i in range(cs_violation.shape[0]):
        resset_data = cs_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        # if (symbol, sheet_year) in [('000670.SZ', 2015)]:
        # ('000504.SZ', 2012),
        # ('000519.SZ', 2014),
        # ('000519.SZ', 2015),]:
        # continue
        wind_data = violation_cs.loc[(violation_cs.symbol == symbol) & (violation_cs.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['经营活动产生的现金流量净额()_NetOpCashFl'] - wind_data['NET_CASH_FLOWS_OPER_ACT'] == 0
        except AssertionError:
            m = m + 1


def wind_violation_data_update():
    os.chdir(resset_path)
    bs_data = pd.read_excel('资产负债表.xls')
    bs_data['symbol'] = bs_data['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3'] else str(x).zfill(6) + '.SH')
    bs_data['sheet_year'] = bs_data['截止日期_EndDt'].apply(lambda x: x.year)
    is_data = pd.read_excel('利润表.xls')
    is_data['symbol'] = is_data['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3'] else str(x).zfill(6) + '.SH')
    is_data['sheet_year'] = is_data['截止日期_EndDt'].apply(lambda x: x.year)
    cs_data = pd.read_excel('现金流量表.xls')
    cs_data['symbol'] = cs_data['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3'] else str(x).zfill(6) + '.SH')
    cs_data['sheet_year'] = cs_data['截止日期_EndDt'].apply(lambda x: x.year)
    fa_depreciation = pd.read_excel('固定资产折旧.xls')
    fa_depreciation = fa_depreciation.loc[fa_depreciation['固定资产名称_FixAssNm'] == '合计',].reset_index(drop=True)
    fa_depreciation['symbol'] = fa_depreciation['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3'] else str(x).zfill(6) + '.SH')
    fa_depreciation['sheet_year'] = fa_depreciation['截止日期_EndDt'].apply(lambda x: x.year)

    violation = pd.read_excel('../violation_symbol_industry.xlsx')
    # violation = violation.loc[(violation.violation_year >= 2005) & (violation.violation_year <= 2019),]
    bs_violation = bs_data.loc[(bs_data['会计准则_AccStd'] == 1) & (bs_data['调整标识()_AdjFlg'] == 0),]
    bs_violation = bs_violation.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: x.sort_values(by=['信息发布日期_InfoPubDt']).iloc[0,]).reset_index(drop=True)
    bs_violation = violation.merge(bs_violation, on=['symbol', 'sheet_year'], how='inner')
    assert bs_violation[['symbol', 'sheet_year']].drop_duplicates().__len__() == bs_violation.__len__()
    is_violation = is_data.loc[(is_data['会计准则()_AccStd'] == 1) & (is_data['调整标识()_AdjFlg'] == 0),]
    is_violation = is_violation.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: x.sort_values(by=['信息发布日期_InfoPubDt']).iloc[0,]).reset_index(drop=True)
    is_violation = violation.merge(is_violation, on=['symbol', 'sheet_year'], how='inner')
    assert is_violation[['symbol', 'sheet_year']].drop_duplicates().__len__() == is_violation.__len__()
    cs_violation = cs_data.loc[(cs_data['会计准则()_AccStd'] == 1) & (cs_data['调整标识()_AdjFlg'] == 0),]
    cs_violation = cs_violation.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: x.sort_values(by=['信息发布日期_InfoPubDt']).iloc[0,]).reset_index(drop=True)
    cs_violation = violation.merge(cs_violation, on=['symbol', 'sheet_year'], how='inner')
    assert cs_violation[['symbol', 'sheet_year']].drop_duplicates().__len__() == cs_violation.__len__()
    fa_depreciation_violation = violation.merge(fa_depreciation, on=['symbol', 'sheet_year'], how='inner')
    assert fa_depreciation_violation[
               ['symbol', 'sheet_year']].drop_duplicates().__len__() == fa_depreciation_violation.__len__()

    os.chdir('../Wind数据库')
    all_bs = pd.read_excel('all_bs_wind.xlsx')
    all_is = pd.read_excel('all_is_wind.xlsx')
    all_cs = pd.read_excel('all_cs_wind.xlsx')

    os.chdir(data_path)
    violation = pd.read_excel('violation_symbol_industry.xlsx')
    violation_bs = violation.merge(all_bs, on = ['symbol', 'sheet_year'], how='inner')
    assert len(violation_bs) == len(violation)
    violation_cs = violation.merge(all_cs, on = ['symbol', 'sheet_year'], how='inner')
    assert len(violation_cs) == len(violation)
    violation_is = violation.merge(all_is, on = ['symbol', 'sheet_year'], how='inner')
    assert len(violation_is) == len(violation)
    m = 0
    for i in range(bs_violation.shape[0]):
        resset_data = bs_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        wind_data = violation_bs.loc[(violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['货币资金(元)_CashEqv'] - wind_data['MONETARY_CAP'] == 0
            assert resset_data['应收账款(元)_AccRec'] - wind_data['ACCT_RCV'] == 0
            if not pd.isna(resset_data['其他应收款(元)_OthRec']):
                assert resset_data['其他应收款(元)_OthRec'] - wind_data['OTH_RCV_TOT'] == 0
            if not pd.isna(resset_data['存货(元)_Inventories']):
                assert resset_data['存货(元)_Inventories'] - wind_data['INVENTORIES'] == 0
            assert resset_data['流动资产合计(元)_TotCurrAss'] - wind_data['TOT_CUR_ASSETS'] == 0
            assert resset_data['资产总计(元)_TotAss'] - wind_data['TOT_ASSETS'] == 0
            if not pd.isna(resset_data['应付股利(元)_DividPay']):
                assert resset_data['应付股利(元)_DividPay'] - wind_data['DVD_PAYABLE'] == 0
            if not pd.isna(resset_data['应交税费(元)_TaxPay']):
                assert resset_data['应交税费(元)_TaxPay'] - wind_data['TAXES_SURCHARGES_PAYABLE'] == 0
            if not pd.isna(resset_data['一年内到期的非流动负债(元)_NCurrLiabOne']):
                assert resset_data['一年内到期的非流动负债(元)_NCurrLiabOne'] - wind_data['NON_CUR_LIAB_DUE_WITHIN_1Y'] == 0
            assert resset_data['流动负债合计(元)_TotCurLia'] - wind_data['TOT_CUR_LIAB'] == 0
            assert resset_data['非流动负债合计(元)_TotNCurLia'] - wind_data['TOT_NON_CUR_LIAB'] == 0
            assert resset_data['负债合计(元)_TotLiab'] - wind_data['TOT_LIAB'] == 0
            assert resset_data['所有者权益（或股东权益）合计(元)_TotShareEquit'] - wind_data['TOT_EQUITY'] == 0
        except AssertionError:
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'MONETARY_CAP'] = \
                resset_data['货币资金(元)_CashEqv']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'ACCT_RCV'] = \
                resset_data['应收账款(元)_AccRec']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'OTH_RCV_TOT'] = \
                resset_data['其他应收款(元)_OthRec']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'INVENTORIES'] = \
                resset_data['存货(元)_Inventories']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_CUR_ASSETS'] = \
                resset_data['流动资产合计(元)_TotCurrAss']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_ASSETS'] = \
                resset_data['资产总计(元)_TotAss']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'DVD_PAYABLE'] = \
                resset_data['应付股利(元)_DividPay']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TAXES_SURCHARGES_PAYABLE'] = \
                resset_data['应交税费(元)_TaxPay']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (
                        violation_bs.sheet_year == sheet_year), 'NON_CUR_LIAB_DUE_WITHIN_1Y'] = \
                resset_data['一年内到期的非流动负债(元)_NCurrLiabOne']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_CUR_LIAB'] = \
                resset_data['流动负债合计(元)_TotCurLia']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_NON_CUR_LIAB'] = \
                resset_data['非流动负债合计(元)_TotNCurLia']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_LIAB'] = \
                resset_data['负债合计(元)_TotLiab']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'TOT_EQUITY'] = \
                resset_data['所有者权益（或股东权益）合计(元)_TotShareEquit']
            m = m + 1
    print(m)

    m = 0
    for i in range(fa_depreciation_violation.shape[0]):
        resset_data = fa_depreciation_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        wind_data = violation_bs.loc[(violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            if not pd.isna(resset_data['累计折旧期末数(元)_EndAccuDepr']):
                assert resset_data['累计折旧期末数(元)_EndAccuDepr'] - wind_data['STMNOTE_ASSETDETAIL_2'] == 0
            if not pd.isna(resset_data['原值期末数(元)_EndOrCost']):
                assert resset_data['原值期末数(元)_EndOrCost'] - wind_data['STMNOTE_ASSETDETAIL_1'] == 0
        except AssertionError:
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'STMNOTE_ASSETDETAIL_2'] = \
                resset_data['累计折旧期末数(元)_EndAccuDepr']
            violation_bs.loc[
                (violation_bs.symbol == symbol) & (violation_bs.sheet_year == sheet_year), 'STMNOTE_ASSETDETAIL_1'] = \
                resset_data['原值期末数(元)_EndOrCost']
            m = m + 1
    print(m)
    violation_bs.to_excel('violation_bs.xlsx', index=False)

    m = 0
    for i in range(is_violation.shape[0]):
        resset_data = is_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        wind_data = violation_is.loc[(violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['利润总额()_TotProf'] - wind_data['TOT_PROFIT'] == 0
            assert resset_data['财务费用()_FinanExp'] - wind_data['FIN_EXP_IS'] == 0
            assert resset_data['营业成本()_OpCost'] - wind_data['OPER_COST'] == 0
            assert resset_data['营业总收入()_TotOpRev'] - wind_data['TOT_OPER_REV'] == 0
            assert resset_data['净利润()_NetProf'] - wind_data['NET_PROFIT_IS'] == 0
            assert resset_data['营业收入()_OpRev'] - wind_data['OPER_REV'] == 0
        except AssertionError:
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'TOT_PROFIT'] = \
                resset_data['利润总额()_TotProf']
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'FIN_EXP_IS'] = \
                resset_data['财务费用()_FinanExp']
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'OPER_COST'] = \
                resset_data['营业成本()_OpCost']
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'TOT_OPER_REV'] = \
                resset_data['营业总收入()_TotOpRev']
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'NET_PROFIT_IS'] = \
                resset_data['净利润()_NetProf']
            violation_is.loc[
                (violation_is.symbol == symbol) & (violation_is.sheet_year == sheet_year), 'OPER_REV'] = \
                resset_data['营业收入()_OpRev']
            m = m + 1
    print(m)
    violation_is.to_excel('violation_is.xlsx', index=False)

    m = 0
    for i in range(cs_violation.shape[0]):
        resset_data = cs_violation.iloc[i,]
        symbol = resset_data.loc['symbol']
        sheet_year = resset_data.loc['sheet_year']
        wind_data = violation_cs.loc[(violation_cs.symbol == symbol) & (violation_cs.sheet_year == sheet_year), :].iloc[
            0,]
        try:
            assert resset_data['经营活动产生的现金流量净额()_NetOpCashFl'] - wind_data['NET_CASH_FLOWS_OPER_ACT'] == 0
        except AssertionError:
            violation_cs.loc[
                (violation_cs.symbol == symbol) & (violation_cs.sheet_year == sheet_year), 'NET_CASH_FLOWS_OPER_ACT'] = \
                resset_data['经营活动产生的现金流量净额()_NetOpCashFl']
            m = m + 1
    print(m)
    violation_cs.to_excel('violation_cs.xlsx', index=False)


def other_factors_build():
    os.chdir(data_path)
    violation = pd.read_excel('violation_symbol_industry.xlsx')
    all = pd.read_excel('stock_all_symbol_industry.xlsx')

    os.chdir(resset_path)
    data1 = pd.read_excel('关联交易.xls')
    data1 = data1[data1.年末标识_YrFlg == 1]
    data1['symbol'] = data1['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data1['sheet_year'] = data1['截止日期_EndDt'].apply(lambda x: x.year)
    data1 = data1.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: x['交易金额(元)_TrdSum'].sum()).reset_index(drop=False).rename(columns={0: '关联交易金额'})
    violation_other = violation.merge(data1, on=['symbol', 'sheet_year'], how='left')
    all_other = all.merge(data1, on=['symbol', 'sheet_year'], how='left')
    violation_other['关联交易金额'].fillna(value=0, inplace=True)
    all_other['关联交易金额'].fillna(value=0, inplace=True)

    data2 = pd.read_excel('再融资信息.xls')
    data2 = data2[data2['是否实施_IfImpl'] == 1]
    data2['symbol'] = data2['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data2['sheet_year'] = data2['信息发布日期_InfoPubDt'].apply(lambda x: x.year)
    data2 = data2.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: 1).reset_index(drop=False).rename(columns={0: '是否再融资'})
    data2 = data2[['symbol', 'sheet_year', '是否再融资']]
    violation_other = violation_other.merge(data2, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data2, on=['symbol', 'sheet_year'], how='left')
    violation_other['是否再融资'].fillna(value=0, inplace=True)
    all_other['是否再融资'].fillna(value=0, inplace=True)

    data3 = pd.DataFrame()
    for i in range(1,4):
        data3 = data3.append(pd.read_excel(f'审计意见{i}.xls'), ignore_index=True)
    data3 = data3.loc[data3['截止日期_Enddt'].apply(lambda x: x.strftime('%Y-%m-%d').split('-')[1])=='12',]
    data3.loc[data3['审计意见类型_OpiType'] != 1, '是否非标准审计意见'] = 1
    data3.loc[data3['审计意见类型_OpiType'] == 1, '是否非标准审计意见'] = 0
    data3['会计师事务所'] = data3['会计师事务所_AccFir'].apply(lambda x: str(x).replace('\u3000', '').replace('(特殊普通合伙)', '').replace('(普通特殊合伙)', ''))
    data3['symbol'] = data3['A股股票代码_A_Stkcd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data3['sheet_year'] = data3['截止日期_Enddt'].apply(lambda x: x.year)
    data3 = data3[['symbol', 'sheet_year', '是否非标准审计意见', '会计师事务所']]
    violation_other = violation_other.merge(data3, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data3, on=['symbol', 'sheet_year'], how='left')
    # violation_other['是否非标准审计意见'].fillna(value=0, inplace=True)
    # all_other['是否非标准审计意见'].fillna(value=0, inplace=True)

    data4 = pd.DataFrame()
    for i in range(1,9):
        data4 = data4.append(pd.read_excel(f'月换手率{i}.xls'), ignore_index=True)
    data4['symbol'] = data4['股票代码_Stkcd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data4['sheet_year'] = data4['日期_Date'].apply(lambda x: x.year)
    data4 = data4.groupby(by=['symbol', 'sheet_year'], group_keys=False).apply(
        lambda x: x['总股数月换手率()_MonFulTurnR'].std(skipna=True) if len(
            x['总股数月换手率()_MonFulTurnR']) >= 3 else 0).reset_index(drop=False).rename(columns={0: '股票月换手率波动率'})
    violation_other = violation_other.merge(data4, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data4, on=['symbol', 'sheet_year'], how='left')
    # violation_other['股票月换手率波动率'].fillna(value=0, inplace=True)
    # all_other['股票月换手率波动率'].fillna(value=0, inplace=True)


    data5 = pd.DataFrame()
    for i in range(1,4):
        data5 = data5.append(pd.read_excel(f'机构投资者持股{i}.xls'), ignore_index=True)
    data5 = data5.loc[data5['截止日期_EndDt'].apply(lambda x: x.strftime('%Y-%m-%d').split('-')[1])=='12',]
    data5['symbol'] = data5['股票代码_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data5['sheet_year'] = data5['截止日期_EndDt'].apply(lambda x: x.year)
    data5['机构投资者持股比例'] = data5['机构投资者持股比例_TotInsHoldper']
    data5 = data5[['symbol', 'sheet_year', '机构投资者持股比例']]
    violation_other = violation_other.merge(data5, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data5, on=['symbol', 'sheet_year'], how='left')
    # violation_other['机构投资者持股比例'].fillna(value=0, inplace=True)
    # all_other['机构投资者持股比例'].fillna(value=0, inplace=True)

    data6 = pd.read_excel('股市周期.xls')
    data6 = data6.loc[(data6['交易所标识_Exchflg'] == 0) & (data6['市场标识_Mktflg'] == 'AB'),]
    data6['sheet_year'] = data6['日期_Date'].apply(lambda x: x.year)
    data6['等权平均市场年收益率'] = data6['等权平均市场年收益率_Yreteq']
    data6 = data6[['sheet_year', '等权平均市场年收益率']]
    violation_other = violation_other.merge(data6, on=['sheet_year'], how='left')
    all_other = all_other.merge(data6, on=['sheet_year'], how='left')

    data7 = pd.read_excel('股权集中度.xls')
    data7 = data7.loc[data7['年末标识_YrFlg'] == 1,]
    data7['symbol'] = data7['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data7['sheet_year'] = data7['截止日期_EndDt'].apply(lambda x: x.year)
    data7['H5指数'] = data7['H5指数()_H5Index']
    data7['Z指数'] = data7['Z指数()_ZIndex']
    data7['国有股比例'] = data7['国有股比例(%)_StateShrPct']
    data7 = data7[['symbol', 'sheet_year', 'H5指数', 'Z指数', '国有股比例']]
    violation_other = violation_other.merge(data7, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data7, on=['symbol', 'sheet_year'], how='left')
    # violation_other['H5指数'].fillna(value=0, inplace=True)
    # violation_other['Z指数'].fillna(value=0, inplace=True)
    # violation_other['国有股比例'].fillna(value=0, inplace=True)
    # all_other['H5指数'].fillna(value=0, inplace=True)
    # all_other['Z指数'].fillna(value=0, inplace=True)
    # all_other['国有股比例'].fillna(value=0, inplace=True)

    data8 = pd.read_excel('董事会.xls')
    data8['symbol'] = data8['A股股票代码_A_StkCd'].apply(
        lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3', '2'] else str(x).zfill(6) + '.SH')
    data8['sheet_year'] = data8['日期_Date'].apply(lambda x: x.year)
    data8['董事长'] = data8['董事长姓名_BdChrNm']
    data8['监事会人数'] = data8['监事会人数_SupNum']
    data8 = data8[['symbol', 'sheet_year', '董事长', '监事会人数']]
    violation_other = violation_other.merge(data8, on=['symbol', 'sheet_year'], how='left')
    all_other = all_other.merge(data8, on=['symbol', 'sheet_year'], how='left')


    os.chdir(data_path)
    violation_other.to_excel('violation_other.xlsx', index=False)
    all_other.to_excel('all_other.xlsx', index=False)

def wind_all_data_update():
    os.chdir(wind_path)
    all_bs = pd.read_excel('all_bs_wind.xlsx')
    all_cs = pd.read_excel('all_cs_wind.xlsx')
    all_is = pd.read_excel('all_is_wind.xlsx')
    os.chdir(data_path)
    all_other = pd.read_excel('all_other.xlsx')

    all_violation_year = pd.read_excel('stock_all_symbol_industry.xlsx')[['symbol', 'sheet_year']]
    all_violation_year['violation_year'] = all_violation_year['sheet_year']
    all_violation_year['sheet_year_0'] = all_violation_year['violation_year']
    all_violation_year['sheet_year_1'] = all_violation_year['violation_year'] - 1
    all_violation_year['sheet_year_2'] = all_violation_year['violation_year'] - 2

    all_symbol_year = pd.DataFrame()
    all_symbol_year = all_symbol_year.append(all_violation_year[['symbol', 'violation_year', 'sheet_year_0']].rename(columns={'sheet_year_0': 'sheet_year'}), ignore_index=True)
    all_symbol_year = all_symbol_year.append(all_violation_year[['symbol', 'violation_year', 'sheet_year_1']].rename(columns={'sheet_year_1': 'sheet_year'}), ignore_index=True)
    all_symbol_year = all_symbol_year.append(all_violation_year[['symbol', 'violation_year', 'sheet_year_2']].rename(columns={'sheet_year_2': 'sheet_year'}), ignore_index=True)
    all_symbol_year = all_symbol_year.sort_values(by=['symbol', 'violation_year', 'sheet_year']).reset_index(drop=True)

    all_bs = all_symbol_year.merge(all_bs, on=['symbol', 'sheet_year'], how='inner')
    all_bs = all_bs.groupby(by=['symbol','violation_year']).apply(lambda x: x if len(x) == 3 else None)
    all_cs = all_symbol_year.merge(all_cs, on=['symbol', 'sheet_year'], how='inner')
    all_cs = all_cs.groupby(by=['symbol','violation_year']).apply(lambda x: x if len(x) == 3 else None)
    all_is = all_symbol_year.merge(all_is, on=['symbol', 'sheet_year'], how='inner')
    all_is = all_is.groupby(by=['symbol','violation_year']).apply(lambda x: x if len(x) == 3 else None)
    all_other = all_symbol_year.merge(all_other, on=['symbol', 'sheet_year'], how='inner')
    all_other = all_other.groupby(by=['symbol','violation_year']).apply(lambda x: x if len(x) == 3 else None)
    all_bs = all_bs.sort_values(by=['symbol', 'violation_year', 'sheet_year']).reset_index(drop=True)
    all_cs = all_cs.sort_values(by=['symbol', 'violation_year', 'sheet_year']).reset_index(drop=True)
    all_is = all_is.sort_values(by=['symbol', 'violation_year', 'sheet_year']).reset_index(drop=True)
    all_other = all_other.sort_values(by=['symbol', 'violation_year', 'sheet_year']).reset_index(drop=True)

    all_bs.to_excel('all_bs.xlsx', index=False)
    all_cs.to_excel('all_cs.xlsx', index=False)
    all_is.to_excel('all_is.xlsx', index=False)
    all_other.to_excel('all_other.xlsx', index=False)

if __name__ == '__main__':
    wind_violation_data_update()
    other_factors_build()
    wind_all_data_update()