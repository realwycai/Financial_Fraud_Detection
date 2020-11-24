# -*- coding: utf-8 -*- 
"""
author: Kyle Cai
e-mail: wycai@pku.edu.cn
"""

import pandas as pd
import os
from functools import wraps, partial

if os.name == 'nt':
    from WindPy import w


class WSSData():
    def __init__(self, symbol, field):
        self.symbol = symbol
        self.field = field

    def fetch_data(self, option) -> pd.DataFrame:
        df = w.wss(self.symbol, self.field, option, usedf=True)
        if df[0] != 0:
            raise RuntimeError(f'{df[1]}')
        return df[1]

def format_processing1(x):
    try:
        temp = str(x).split(',')
        temp.sort(key=lambda y: int(y))
        return temp
    except Exception:
        return None

def potential_fraud_filter():
    violation = pd.read_excel('../../违规数据库1994-2020/STK_Violation_Main.xlsx', header=1).reset_index(drop=True)
    violation['ViolationTypeID'] = violation['ViolationTypeID'].apply(lambda x: x.split(','))
    violation['violation_year'] = violation['ViolationYear'].apply(format_processing1)
    violation_new = pd.DataFrame()
    for i in range(len(violation)):
        # if [x for x in violation.iloc[i,]['ViolationTypeID'] if x in ['P2501', 'P2502', 'P2503', 'P2504', 'P2505', 'P2506', 'P2509', 'P2515']]:
        if [x for x in violation.iloc[i,]['ViolationTypeID'] if x in ['P2501', 'P2502']]:
            try:
                if int(violation.iloc[i, ]['violation_year'][0]) >= 2000:
                    violation_new = violation_new.append(violation.iloc[i,])
            except Exception:
                pass
    violation_new = violation_new.rename(columns={'Symbol': 'symbol'})
    violation_new['symbol'] = violation_new['symbol'].apply(lambda x: str(x).zfill(6) + '.SZ' if str(x).zfill(6)[0] in ['0', '3'] else str(x).zfill(6) + '.SH')
    violation_new.to_excel('fraud_company.xlsx', index=False)

def violation_company_symbol_year() -> pd.DataFrame:
    violation = pd.read_excel('fraud_company_修正后.xlsx')
    violation_concise = violation.loc[:, ['symbol', 'ViolationYear']]
    violation_concise['violation_year'] = violation_concise.ViolationYear.apply(lambda x: int(format_processing1(x)[0]))
    violation_concise['violation_year_last'] = violation_concise.ViolationYear.apply(lambda x: int(format_processing1(x)[-1]))

    for i in range(len(violation_concise)):
        # if Date(violation_concise.iloc[i,]['STM_ISSUINGDATE'].strftime('%Y-%m-%d')) > Date(violation_concise.iloc[i,]['DisposalDate']):
        #     violation_concise.loc[i, 'start_year'] = int(violation_concise.loc[i, 'violation_year']-4)
        #     violation_concise.loc[i, 'end_year'] = int(violation_concise.loc[i, 'violation_year']-2)
        # else:
        #     violation_concise.loc[i, 'start_year'] = int(violation_concise.loc[i, 'disposal_year']-3)
        #     violation_concise.loc[i, 'end_year'] = int(violation_concise.loc[i, 'disposal_year']-1)
        violation_concise.loc[i, 'start_year'] = int(violation_concise.loc[i, 'violation_year'] - 2)
        violation_concise.loc[i, 'end_year'] = int(violation_concise.loc[i, 'violation_year'])
    violation_concise = violation_concise[['symbol', 'start_year', 'end_year', 'violation_year', 'violation_year_last']]
    violation_concise = violation_concise.drop_duplicates().reset_index(drop=True)

    # 如果公司的被处理事件的财务报表数据集有重合，则只留下首次被处理的财务报表。
    def end_year_handle(data_inner: pd.DataFrame):
        data_new = pd.DataFrame(columns=['symbol', 'start_year', 'end_year', 'violation_year'])
        data_new = data_new.append(data_inner.iloc[0,], ignore_index=True)
        for i in range(1, len(data_inner)):
            if data_inner.iloc[i,]['start_year'] <= data_new.iloc[-1,]['violation_year_last']:
                pass
            else:
                data_new = data_new.append(data_inner.iloc[i,], ignore_index=True)
        return data_new

    violation_concise = violation_concise.sort_values(by=['symbol', 'start_year', 'violation_year_last']).reset_index(drop=True)
    violation_concise = violation_concise.groupby(by='symbol', group_keys=False).apply(end_year_handle)

    def sheet_year(data_inner: pd.DataFrame):
        if len(data_inner)>1:
            raise AssertionError
        data_inner = data_inner.iloc[0,]
        data_new = pd.DataFrame(columns=['symbol', 'sheet_year', 'violation_year'])
        for year in range(int(data_inner['start_year']), int(data_inner['end_year'] + 1)):
            data_new = data_new.append(
                {'symbol': data_inner['symbol'], 'sheet_year': year, 'violation_year': data_inner['violation_year']},
                ignore_index=True)
        return data_new

    violation_concise = violation_concise.sort_values(by=['symbol', 'start_year']).reset_index(drop=True)
    violation_concise = violation_concise.groupby(by=['symbol', 'violation_year'], group_keys=False).apply(sheet_year)
    return violation_concise


def wind_symbol_decorator(fun):
    @wraps(fun)
    def wrap(data: pd.DataFrame, group_target: str, **kwargs):
        w.start()
        data = data.groupby(by=group_target, group_keys=False).apply(partial(fun, **kwargs)).reset_index(drop=True)
        w.close()
        return data
    return wrap

@wind_symbol_decorator
def announcement_date_handle(data_inner: pd.DataFrame, **kwargs) -> pd.DataFrame:
    industry = WSSData(symbol=','.join(data_inner.loc[:,'symbol'].unique()), field="stm_issuingdate,stm_rpt_e")
    year = data_inner.iloc[0, ]['disposal_year']
    bs_data = industry.fetch_data(f"rptDate={year-1}1231;dataType=0").reset_index(drop=False).rename(columns={'index':'symbol'})
    bs_data = data_inner.merge(bs_data, on='symbol')
    print(f"{year} finished.")
    return bs_data

def format_processing2(x):
    try:
        return x.strftime('%Y-%m-%d')
    except Exception:
        return x

@wind_symbol_decorator
def industry_handle(data_inner: pd.DataFrame, **kwargs) -> pd.DataFrame:
    industry = WSSData(symbol=','.join(data_inner.loc[:,'symbol'].unique()), field='industry_citic,industry_csrc12_n,ipo_date,delist_date')
    year = data_inner.iloc[0, ]['sheet_year']
    industry_data = industry.fetch_data(f"tradeDate={year}1231;industryType=1").reset_index(drop=False).rename(columns={'index':'symbol'})
    industry_data = industry_data.merge(data_inner, on='symbol')
    industry_data['IPO_DATE'] = industry_data['IPO_DATE'].apply(format_processing2)
    industry_data['DELIST_DATE'] = industry_data['DELIST_DATE'].apply(format_processing2)
    print(f"{year} finished.")
    return industry_data

@wind_symbol_decorator
def CSI300_financial_statement_handle(data_inner: pd.DataFrame, field) -> pd.DataFrame:
    industry = WSSData(symbol=','.join(data_inner.loc[:,'symbol'].unique()), field=field)
    year = data_inner.iloc[0, ]['sheet_year']
    bs_data = industry.fetch_data(f"unit=1;rptDate={year}1231;rptType=3").reset_index(drop=False).rename(columns={'index':'symbol'})
    bs_data = bs_data.merge(data_inner, on='symbol')
    print(f"{year} finished.")
    return bs_data

@wind_symbol_decorator
def financial_statement_handle(data_inner: pd.DataFrame, field) -> pd.DataFrame:
    industry = WSSData(symbol=','.join(data_inner.loc[:,'symbol'].unique()), field=field)
    year = data_inner.iloc[0, ]['sheet_year']
    bs_data = industry.fetch_data(f"unit=1;rptDate={year}1231;rptType=1").reset_index(drop=False).rename(columns={'index':'symbol'})
    bs_data = bs_data.merge(data_inner, on='symbol')
    print(f"{year} finished.")
    return bs_data

if __name__ == '__main__':
    os.chdir("data")
    """
    筛选出可能的违约公司并储存
    """
    # potential_fraud_filter()
    """
    获取违约公司违约前2年的数据
    """
    # violation = violation_company_symbol_year()
    # violation = industry_handle(violation, group_target='sheet_year')
    # violation = violation.sort_values(by=['symbol', 'violation_year', 'sheet_year'])
    # violation = violation.loc[violation['IPO_DATE'].apply(lambda x: int(x[:4]))<violation['violation_year'],]
    # violation = violation[violation['violation_year']>=2007]
    # violation.to_excel('violation_symbol_industry.xlsx', index=False)
    """
    获取违约公司财务报表
    """
    # violation = pd.read_excel('violation_symbol_industry.xlsx')
    # bs_violation = financial_statement_handle(violation, group_target='sheet_year', field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_violation.to_excel('./Wind数据库/violation_bs_未调整.xlsx', index=False)
    # is_violation = financial_statement_handle(violation, group_target='sheet_year', field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV, DEDUCTEDPROFIT')
    # is_violation.to_excel('./Wind数据库/violation_is_未调整.xlsx', index=False)
    # cs_violation = financial_statement_handle(violation, group_target='sheet_year', field='NET_CASH_FLOWS_OPER_ACT')
    # cs_violation.to_excel('./Wind数据库/violation_cs_未调整.xlsx', index=False)
    """
    获取沪深300指数成分
    """
    # stock_CSI300 = pd.DataFrame(columns=['sheet_year', 'violation_year', 'symbol'])
    # w.start()
    # for year in range(2005, 2020):
    #     df:pd.DataFrame = w.wset("sectorconstituent",f"date={year}-12-31;windcode=000300.SH", usedf=True)
    #     if df[0] != 0:
    #         raise RuntimeError('Fetching data failed.')
    #     data1 = df[1].copy(deep=True)
    #     data1['sheet_year'] = year
    #     data2 = df[1].copy(deep=True)
    #     data2['sheet_year'] = year-1
    #     data3 = df[1].copy(deep=True)
    #     data3['sheet_year'] = year-2
    #     data = pd.concat([data1, data2, data3], axis=0)
    #     data = data.rename(columns={'wind_code':'symbol'})
    #     data['violation_year'] = year
    #     stock_CSI300 = stock_CSI300.append(data[['symbol', 'sheet_year', 'violation_year']], ignore_index=True)
    # w.close()
    # stock_CSI300 = industry_handle(stock_CSI300, group_target='sheet_year')
    # stock_CSI300 = stock_CSI300.sort_values(by=['violation_year', 'sheet_year', 'symbol'])
    # stock_CSI300.to_excel('CSI300_symbol_industry.xlsx', index=False)
    # """
    #  获取沪深300公司的财务报表
    #  """
    # stock_CSI300 = pd.read_excel('CSI300_symbol_industry.xlsx')
    # stock_CSI300 = stock_CSI300[['symbol', 'sheet_year', 'DELIST_DATE']].drop_duplicates()
    # stock_CSI300_1 = stock_CSI300.loc[(stock_CSI300['sheet_year'] < 2019) & (
    #             (stock_CSI300['DELIST_DATE'].apply(lambda x: int(x[:4])) - 1 > stock_CSI300['sheet_year']) | (
    #                 stock_CSI300['DELIST_DATE'].apply(lambda x: int(x[:4])) == 1899)),]
    # stock_CSI300_2 = stock_CSI300.loc[(stock_CSI300['sheet_year'] >= 2019) | (
    #             (stock_CSI300['DELIST_DATE'].apply(lambda x: int(x[:4])) - 1 <= stock_CSI300['sheet_year']) & (
    #                 stock_CSI300['DELIST_DATE'].apply(lambda x: int(x[:4])) != 1899)),]
    # bs_stock_CSI300_1 = CSI300_financial_statement_handle(stock_CSI300_1, group_target='sheet_year',
    #                                                       field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_stock_CSI300_2 = financial_statement_handle(stock_CSI300_2, group_target='sheet_year',
    #                                                field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_stock_CSI300 = bs_stock_CSI300_1.append(bs_stock_CSI300_2, ignore_index=True)
    # bs_stock_CSI300.to_excel('CSI300_bs.xlsx', index=False)
    # is_stock_CSI300_1 = CSI300_financial_statement_handle(stock_CSI300_1, group_target='sheet_year',
    #                                                       field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV')
    # is_stock_CSI300_2 = financial_statement_handle(stock_CSI300_2, group_target='sheet_year',
    #                                                field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV')
    # is_stock_CSI300 = is_stock_CSI300_1.append(is_stock_CSI300_2, ignore_index=True)
    # is_stock_CSI300.to_excel('CSI300_is.xlsx', index=False)
    # cs_stock_CSI300_1 = CSI300_financial_statement_handle(stock_CSI300_1, group_target='sheet_year',
    #                                                       field='NET_CASH_FLOWS_OPER_ACT')
    # cs_stock_CSI300_2 = financial_statement_handle(stock_CSI300_2, group_target='sheet_year',
    #                                                field='NET_CASH_FLOWS_OPER_ACT')
    # cs_stock_CSI300 = cs_stock_CSI300_1.append(cs_stock_CSI300_2, ignore_index=True)
    # cs_stock_CSI300.to_excel('CSI300_cs.xlsx', index=False)
    """
        获取全市场成分
    """
    # stock_all = pd.DataFrame(columns=['sheet_year', 'violation_year', 'symbol'])
    # w.start()
    # for year in range(2005, 2020):
    #     df:pd.DataFrame = w.wset("sectorconstituent",f"date={year}-12-31;sectorid=a001010100000000", usedf=True)
    #     if df[0] != 0:
    #         raise RuntimeError('Fetching data failed.')
    #     data = df[1].rename(columns={'wind_code':'symbol'})
    #     data['sheet_year'] = year
    #     stock_all = stock_all.append(data[['symbol', 'sheet_year']], ignore_index=True)
    # w.close()
    # stock_all = industry_handle(stock_all, group_target='sheet_year')
    # stock_all = stock_all.sort_values(by=['sheet_year', 'symbol'])
    # stock_all.to_excel('stock_all_symbol_industry.xlsx', index=False)
    """
       获取全市场公司的财务报表
    """
    # stock_all = pd.read_excel('stock_all_symbol_industry.xlsx')
    # stock_all = stock_all[['symbol', 'sheet_year', 'DELIST_DATE']].drop_duplicates()
    # stock_all_1 = stock_all.loc[(stock_all['sheet_year'] < 2019) & (
    #         (stock_all['DELIST_DATE'].apply(lambda x: int(x[:4])) - 1 > stock_all['sheet_year']) | (
    #         stock_all['DELIST_DATE'].apply(lambda x: int(x[:4])) == 1899)),]
    # stock_all_2 = stock_all.loc[(stock_all['sheet_year'] >= 2019) | (
    #         (stock_all['DELIST_DATE'].apply(lambda x: int(x[:4])) - 1 <= stock_all['sheet_year']) & (
    #         stock_all['DELIST_DATE'].apply(lambda x: int(x[:4])) != 1899)),]
    # bs_stock_all_1 = CSI300_financial_statement_handle(stock_all_1, group_target='sheet_year',
    #                                                       field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_stock_all_2 = financial_statement_handle(stock_all_2, group_target='sheet_year',
    #                                                field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_stock_all = bs_stock_all_1.append(bs_stock_all_2, ignore_index=True)
    # bs_stock_all.to_excel('all_bs.xlsx', index=False)
    # is_stock_all_1 = CSI300_financial_statement_handle(stock_all_1, group_target='sheet_year',
    #                                                       field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV')
    # is_stock_all_2 = financial_statement_handle(stock_all_2, group_target='sheet_year',
    #                                                field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV')
    # is_stock_all = is_stock_all_1.append(is_stock_all_2, ignore_index=True)
    # is_stock_all.to_excel('all_is.xlsx', index=False)
    # cs_stock_all_1 = CSI300_financial_statement_handle(stock_all_1, group_target='sheet_year',
    #                                                       field='NET_CASH_FLOWS_OPER_ACT')
    # cs_stock_all_2 = financial_statement_handle(stock_all_2, group_target='sheet_year',
    #                                                field='NET_CASH_FLOWS_OPER_ACT')
    # cs_stock_all = cs_stock_all_1.append(cs_stock_all_2, ignore_index=True)
    # cs_stock_all.to_excel('all_cs.xlsx', index=False)

    """
    加上未上市时的部分报表
    """
    # os.chdir('全市场作为对照样本相应的数据')
    # violation = pd.read_excel('violation_symbol_industry.xlsx')
    # all = pd.read_excel('stock_all_symbol_industry.xlsx')
    # lost_idx = []
    # for i in range(violation.shape[0]):
    #     if all[
    #         (all.symbol == violation.iloc[i,]['symbol']) & (all.sheet_year == violation.iloc[i,]['sheet_year'])].empty:
    #         lost_idx.append(i)
    # lost = violation.iloc[lost_idx,]
    # bs_stock_lost = CSI300_financial_statement_handle(lost, group_target='sheet_year', field='TOT_CUR_ASSETS, TOT_CUR_LIAB, INVENTORIES, TOT_LIAB, TOT_ASSETS, ACCT_RCV, OTH_RCV_TOT, TOT_EQUITY, TOT_NON_CUR_LIAB, DVD_PAYABLE, STMNOTE_ASSETDETAIL_2, STMNOTE_ASSETDETAIL_1, MONETARY_CAP, NON_CUR_LIAB_DUE_WITHIN_1Y, TAXES_SURCHARGES_PAYABLE')
    # bs_stock_lost.to_excel('bs_stock_lost.xlsx', index=False)
    # is_stock_lost = CSI300_financial_statement_handle(lost, group_target='sheet_year', field='TOT_PROFIT, FIN_EXP_IS, OPER_COST, TOT_OPER_REV, NET_PROFIT_IS, OPER_REV')
    # is_stock_lost.to_excel('is_stock_lost.xlsx', index=False)
    # cs_stock_lost = CSI300_financial_statement_handle(lost, group_target='sheet_year', field='NET_CASH_FLOWS_OPER_ACT')
    # cs_stock_lost.to_excel('cs_stock_lost.xlsx', index=False)