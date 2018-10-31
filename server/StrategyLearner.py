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
from RTLearner import RTLearner
# from DTLearner import DTLearner

class StrategyLearner(object):
    def author(self):
        return "msaqib3"

    # constructor
    def __init__(self, verbose = False, impact=0.0, ybuy=0.00, rfThresh=0.1):
        '''
        verbose
        impact: how much impact does trade have
        ybuy: threshold for buying (and conversely negative for shorting) (generates Y)
        rfThresh: threshold to go all out
        '''
        self.verbose = verbose
        self.impact = impact
        self.ybuy = ybuy
        # self.learner = RTLearner, kwargs={'leaf_size': 5}, bags=3)
        self.learner = RTLearner(leaf_size = 5)
        self.rfThresh = rfThresh


    # this method should create a RTLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):

        # add your code to do learning here

        # example usage of the old backward compatible util function
        syms=[symbol]
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data(syms, dates)  # automatically adds SPY
        prices = prices_all[syms]  # only portfolio symbols
        prices_SPY = prices_all['SPY']  # only SPY, for comparison later
        if self.verbose: print prices

        # example use with new colname
        volume_all = ut.get_data(syms, dates, colname = "Volume")  # automatically adds SPY
        volume = volume_all[symbol]  # only portfolio symbols
        volume_SPY = volume_all['SPY']  # only SPY, for comparison later
        if self.verbose: print volume

        # generate some technical statistics on stock data



        X, Y = self.genStats(prices[symbol], volume)
        # print(Y)



        self.learner.addEvidence(X, Y)

    def genStats(self, price, volume):
        '''
        Generates X and Y for data
        '''
        # prices_all["Y"] = Y
        changeVol = (volume.iloc[0] - volume) / volume.iloc[0]
        changeVol = changeVol.fillna(method="ffill").fillna(method="bfill")
        dr = (price.shift(-1)) / price - 1 #return for 1 day in future if you invested today
        prices = pd.DataFrame(price)

        # print  "dr", dr.mean()
        dr = dr.fillna(method='ffill').fillna(method="bfill")
        if self.impact != 0:
            threeDayRet = (price.shift(-5)) / price - 1
            threeDayRet = threeDayRet.fillna(method="ffill").fillna(method="bfill")
            Y = threeDayRet.apply(lambda x: 1 if x > (self.ybuy + 6 * self.impact) else -1 if x < (-self.ybuy - 6 * self.impact) else np.nan) #predict future dr from past!
            Y = Y.fillna(method="ffill", limit=3)
            Y = Y.fillna(0)
            # Y = Y.rolling(2)
            if pd.isnull(Y.iloc[0]):
                Y.iloc[0] = 0
            Y = Y.fillna(method="ffill").fillna(method="bfill")
        else:
            Y = dr.apply(lambda x: 1 if x > (self.ybuy + self.impact) else -1 if x < (-self.ybuy - self.impact) else 0) #predict future dr from past!
        # Y = (dr - dr.min()) / (dr.max() - dr.min()) * 2 - 1
        # Y = dr.rolling(2).apply(lambda x: if (1-self.impact) * (x.iloc[1] - x.iloc[0])
        momentum = (dr.shift(1) - dr) / dr
        momentum = momentum.fillna(method="ffill").fillna(method="bfill")

        movingAverage = price.rolling(5).mean().fillna(method ="bfill").fillna(method="ffill")
        movingStd = price.rolling(5).std().fillna(method="bfill").fillna(method="ffill")
        moving_z_score = (price - movingAverage) / movingStd
        movingVolStd = volume.rolling(5).std().fillna(method='bfill').fillna(method='ffill')
        X = pd.DataFrame([moving_z_score, movingStd, momentum, changeVol, movingVolStd]).values
        return X.T, Y

    # this method should use the existing policy and test it against new data
    def testPolicy(self, symbol = "IBM", \
        sd=dt.datetime(2009,1,1), \
        ed=dt.datetime(2010,1,1), \
        sv = 10000):

        # print(self.impact)

        # here we build a fake set of trades
        # your code should return the same sort of data
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        volumes_all = ut.get_data([symbol], dates, colname = "Volume")
        X, _ = self.genStats(prices_all[symbol], volumes_all[symbol])
        Ypred = self.learner.query(X)
        Ypred = pd.Series(Ypred, index=prices_all.index)

        # print(X.shape, Ypred)
        trades = prices_all[[symbol,]]  # only portfolio symbols
        # print("trades shape", trades.shape)
        prices = prices_all[symbol]

        trades_SPY = prices_all['SPY']  # only SPY, for comparison later
        trades.values[:,:] = 0 # set them all to nothing
        trades.loc[trades.index[1:], symbol] = Ypred[1:].apply(lambda x: 1000 if x > self.rfThresh else -1000 if x < - self.rfThresh else 0) #position
        trades.loc[trades.index[-1], symbol] = 0
        trades[symbol] = - (trades.shift(1) - trades) # subtract positions now by positions before to get change to portfolio (trades)
        trades.loc[trades.index[0], symbol] = 0
        # state = 0
        # for date in trades.index[:-1]:
        #     #go long
        #     if Ypred[date] > self.rfThresh and (state != 1000 or state != floor(sv / prices[date])): #go all in!
        #         toGoTo = 1000 #if 1000 < (sv / prices[date]) else floor(sv / prices[date])
        #         trades.loc[date, symbol] = toGoTo - state
        #         state = toGoTo
        #     #go short
        #     elif Ypred[date] < -self.rfThresh and (state != -1000 or state != 0 - floor(sv / prices[date])):
        #         toGoTo = - 1000 #if 1000 < (sv / prices[date]) else - floor(sv / prices[date])
        #         trades.loc[date, symbol] = toGoTo - state
        #         state = toGoTo
        #     #exit stock for now
        #     else:
        #         trades.loc[date, symbol] = - state
        #         state = 0
        # trades.values[-1,:] = 0 - state #exit on the last day

        if self.verbose: print type(trades) # it better be a DataFrame!
        if self.verbose: print trades
        if self.verbose: print prices_all
        if self.verbose: print trades.sum().sum()
        return trades

if __name__=="__main__":
    print "One does not simply think up a strategy"

    sl = StrategyLearner()
    sv = 100000
    sl.addEvidence(symbol="ML4T-220",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
    trades = sl.testPolicy(symbol="ML4T-220",sd=dt.datetime(2010,1,1),ed=dt.datetime(2011,12,31),sv=100000)
    print marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv).iloc[-1]
