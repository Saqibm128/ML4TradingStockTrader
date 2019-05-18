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
        self.learner = ensemble.RandomForestRegressor(150)
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

        X, Y = self.genStats(prices[symbol], volume)
        # print(Y)

        self.learner.fit(X, Y)

    def genStats(self, price, volume):
        '''
        Generates X and Y for data
        '''
        # prices_all["Y"] = Y
        changeVol = (volume.iloc[0] - volume) / volume.iloc[0]
        changeVol = changeVol.fillna(method="ffill").fillna(method="bfill")
        dr = (price.shift(-1)) / price - 1  # return for 1 day in future if you invested today
        prices = pd.DataFrame(price)

        # print  "dr", dr.mean()
        dr = dr.fillna(method='ffill').fillna(method="bfill")
        Y = dr * 100  # percentageReturn
        # Y = (dr - dr.min()) / (dr.max() - dr.min()) * 2 - 1
        # Y = dr.rolling(2).apply(lambda x: if (1-self.impact) * (x.iloc[1] - x.iloc[0])
        drChange = dr.shift(2) - dr.shift(1)
        momentum = (dr.shift(2) - dr.shift(1)) / dr.shift(1)
        momentum = momentum.fillna(method="ffill").fillna(method="bfill")

        movingAverage = price.rolling(5).mean().fillna(method="ffill").fillna(method="bfill")
        movingStd = price.rolling(5).std().fillna(method="ffill").fillna(method="bfill")
        moving_z_score = (price - movingAverage) / movingStd
        movingVolStd = volume.rolling(5).std().fillna(method='ffill').fillna(method='bfill')
        X = pd.DataFrame([moving_z_score, movingStd, momentum, changeVol, movingVolStd, drChange])
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
        X, _ = self.genStats(prices_all[symbol], volumes_all[symbol])
        Ypred = self.learner.predict(X)
        Ypred = pd.Series(Ypred, index=prices_all.index)

        trades = pd.DataFrame(index=dates, columns=[symbol])

        trades.loc[trades.index[1:], symbol] = Ypred[1:].apply(
            lambda x: 1 if x > self.rfThresh else 0 if x < - self.rfThresh else np.nan)  # position
        trades.loc[trades.index[-1], symbol] = 0  # we end at 0 shares
        trades.loc[trades.index[0], symbol] = 0  # we start at 0 shares
        trades = trades.fillna(method="ffill").fillna(method="bfill")
        trades[symbol] = - (trades.shift(
            1) - trades)  # subtract positions now by positions before to get change to portfolio (trades)
        trades[symbol].iloc[0] = 0;
        trades = trades * 1
        return trades


if __name__ == "__main__":
    print("One does not simply think up a strategy")

    sl = SingleStockAnalysis()
    symbol = "GOOG"
    md = dt.datetime(2010, 12, 29)
    ed = dt.datetime(2019, 4, 20)
    prices = ut.get_data([symbol], pd.date_range(md, ed))[symbol]
    sv = prices[md]
    sl.addEvidence(symbol=symbol, sd=dt.datetime(2007, 1, 1), ed=md, sv=sv)
    trades = sl.testPolicy(symbol=symbol, sd=md, ed=ed, sv=sv)
    results = (marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv)[1])
    plt.plot(results.index, results)
    plt.show()
    print("Strategy Percent Return {}".format((results.iloc[-1]/sv - 1) * 100))
    print("Benchmark Percent Return {}".format((prices.iloc[-1]/prices[0] - 1) * 100))
