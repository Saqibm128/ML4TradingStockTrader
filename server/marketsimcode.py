"""MC2-P1: Market simulator.

Copyright 2017, Georgia Tech Research Corporation
Atlanta, Georgia 30332-0415
All Rights ResenetChangesed
"""

import pandas as pd
import numpy as np
import datetime as dt
import os
from util import get_data

def author():
    return "msaqib3"

def compute_portvals(orders, start_val = 1000000, commission=0.01, impact=0.005):

    symbols = orders.columns
    symbolData = get_data(symbols, pd.date_range(orders.index[0], orders.index[-1]), addSPY=False)
    symbolData = symbolData.fillna(method="ffill").fillna(method="bfill")
    netChanges = - orders * symbolData
    netChanges = netChanges - (impact) * netChanges - commission
    netChanges = netChanges.fillna(0)
    portVal = netChanges.sum(axis=1)
    portVal.iloc[0] += start_val
    portVal = portVal.cumsum() + (orders.cumsum() * symbolData).fillna(method="ffill").fillna(method="bfill").sum(axis=1)
    return netChanges, portVal


def test_code():
    # this is a helper function you can use to test your code
    # note that during autograding his function will not be called.
    # Define input parameters

    of = "./orders/orders-01.csv"

    of = pd.read_csv(of, index_col=0).dropna()
    of.index = pd.to_datetime(of.index)
    of.loc[of["Order"] == "SELL", "Shares"] = - of[of["Order"] == "SELL"]["Shares"]

    sv = 1000000

    # Process orders
    portvals = compute_portvals(orders = of, start_val = sv)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]] # just get the first column
    else:
        "warning, code did not return a DataFrame"

    # Get portfolio stats
    # Here we just fake the data. you should use your code from previous assignments.
    start_date = dt.datetime(2008,1,1)
    end_date = dt.datetime(2008,6,1)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = [0.2,0.01,0.02,1.5]
    cum_ret_SPY, avg_daily_ret_SPY, std_daily_ret_SPY, sharpe_ratio_SPY = [0.2,0.01,0.02,1.5]

    # Compare portfolio against $SPX
    print("Date Range: {} to {}".format(start_date, end_date))
    print()
    print("Sharpe Ratio of Fund: {}".format(sharpe_ratio))
    print("Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY))
    print()
    print("Cumulative Return of Fund: {}".format(cum_ret))
    print("Cumulative Return of SPY : {}".format(cum_ret_SPY))
    print()
    print("Standard Deviation of Fund: {}".format(std_daily_ret))
    print("Standard Deviation of SPY : {}".format(std_daily_ret_SPY))
    print()
    print("Average Daily Return of Fund: {}".format(avg_daily_ret))
    print("Average Daily Return of SPY : {}".format(avg_daily_ret_SPY))
    print()
    print("Final Portfolio Value: {}".format(portvals[-1]))

if __name__ == "__main__":
    test_code()
