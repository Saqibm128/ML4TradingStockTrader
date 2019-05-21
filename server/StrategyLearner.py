"""
Template for implementing StrategyLearner  (c) 2016 Tucker Balch
"""

import datetime as dt
import pandas as pd
import numpy as np
import util as ut
import random
import math
import marketsimcode
from math import floor
from sklearn import ensemble
import matplotlib.pyplot as plt


class SingleStockAnalysis(object):
    def author(self):
        return "msaqib3"

    # constructor
    def __init__(self, verbose=False, impact=0.0, ybuy=0.00, rfThresh=0.1):
        '''
        verbose
        impact: how much impact does trade have
        ybuy: threshold for buying (and conversely negative for shorting) (generates Y)
        rfThresh: threshold to go all out
        '''
        self.verbose = verbose
        self.impact = impact
        self.ybuy = ybuy
        self.drLearner = ensemble.RandomForestRegressor(150)
        self.volLearner = ensemble.RandomForestRegressor(150)
        self.rfThresh = rfThresh

    # this method should create a RTLearner, and train it for trading
    def addEvidence(self, symbol="IBM",
                    sd=dt.datetime(2008, 1, 1),
                    ed=dt.datetime(2009, 1, 1),
                    sv=10000):
        # add your code to do learning here

        # example usage of the old backward compatible util function
        syms = [symbol]
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        if self.verbose: print(prices)

        # example use with new colname
        volume_all = ut.get_data(syms, dates, colname="Volume")  # automatically adds SPY
        volume = volume_all[symbol]  # only portfolio symbols

        # generate some technical statistics on stock data
        high = ut.get_data(syms, dates, colname="High", addSPY=False)[symbol]
        low = ut.get_data(syms, dates, colname="Low", addSPY=False)[symbol]

        X, Y = self.genStats(prices[symbol], volume, high, low)
        # print(Y)

        self.drLearner.fit(X, Y)

    def genStats(self, price, volume, high, low):
        '''
        Generates X and Y for data
        '''
        # prices_all["Y"] = Y
        changeVol = (volume.shift(1)) / volume.iloc[0]
        dr = (price.shift(-1)) / price - 1  # return for 1 day in future if you invested today

        # print  "dr", dr.mean()
        dr = dr.fillna(method='ffill').fillna(method="bfill")
        Y = dr * 100  # percentageReturn
        drChange = dr.shift(3) - dr.shift(2) #these are actually adj closed vals, so dr.shift(1) would still use adj close of curr day, leading to info leak
        momentum = (dr.shift(3) - dr.shift(2)) / dr.shift(2)
        momentum = momentum.fillna(method="ffill").fillna(method="bfill")
        intraDaySpread = (high.shift(1) - low.shift(1)) / price

        movingAverage = price.rolling(5).mean().fillna(method="ffill").fillna(method="bfill")
        movingStd = price.rolling(5).std().fillna(method="ffill").fillna(method="bfill")
        moving_z_score = (price - movingAverage) / movingStd
        movingVolStd = volume.rolling(5).std().fillna(method='ffill').fillna(method='bfill')
        X = pd.DataFrame([moving_z_score, movingStd, momentum, changeVol, movingVolStd, drChange, dr.shift(2), intraDaySpread])
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(method='ffill').fillna(method='bfill').values
        return X.T, Y

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol="IBM",
                   sd=dt.datetime(2009, 1, 1),
                   ed=dt.datetime(2010, 1, 1),
                   sv=10000):
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        volumes_all = ut.get_data([symbol], dates, colname="Volume")
        high = ut.get_data([symbol], dates, colname="High", addSPY=False)[symbol]
        low = ut.get_data([symbol], dates, colname="Low", addSPY=False)[symbol]

        X, _ = self.genStats(prices_all[symbol], volumes_all[symbol], high, low)
        Ypred = self.drLearner.predict(X)
        Ypred = pd.Series(Ypred, index=prices_all.index)

        trades = pd.DataFrame(index=dates, columns=[symbol])

        trades.loc[trades.index[1:], symbol] = Ypred[1:].apply(
            lambda x: 1 if x > self.rfThresh else 0 if x < - self.rfThresh else np.nan)  # position
        trades.loc[trades.index[-1], symbol] = 0  # we end at 0 shares
        trades.loc[trades.index[0], symbol] = 0  # we start at 0 shares
        trades = trades.fillna(method="ffill").fillna(method="bfill")
        trades[symbol] = - (trades.shift(
            1) - trades)  # subtract positions now by positions before to get change to portfolio (trades)
        trades[symbol].iloc[0] = 0
        trades = trades * 1
        return trades


if __name__ == "__main__":
    print("One does not simply think up a strategy")

    sl = SingleStockAnalysis()
    symbol = "AAPL"
    sd = dt.datetime(2009, 1, 1)
    md = dt.datetime(2012, 12, 29)
    ed = dt.datetime(2019, 4, 20)
    prices = ut.get_data([symbol], pd.date_range(md, ed))[symbol]
    sv = prices[md]
    sl.addEvidence(symbol=symbol, sd=sd, ed=md - dt.timedelta(days=1), sv=sv)
    # sl.addEvidence(symbol=symbol, sd=md, ed=ed, sv=sv)
    trades = sl.testPolicy(symbol=symbol, sd=md, ed=ed, sv=sv)
    results = (marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv)[1])
    plt.plot(results.index, results/results.iloc[0])
    plt.plot(prices.index, prices/prices.iloc[0])
    plt.legend(["Learner", "Benchmark"])
    plt.show()
    print("Strategy Percent Return {}".format((results.iloc[-1]/sv - 1) * 100))
    print("Benchmark Percent Return {}".format((prices.iloc[-1]/prices[0] - 1) * 100))
