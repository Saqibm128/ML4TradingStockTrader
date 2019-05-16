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
from BagLearner import BagLearner
from RTLearner import RTLearner
# from DTLearner import DTLearner

class ManualStrategy(object):
    def author(self):
        return "msaqib3"

    # constructor
    def __init__(self, verbose = False, impact=0.0,):
        '''
        verbose
        impact: how much impact does trade have
        ybuy: threshold for buying (and conversely negative for shorting) (generates Y)
        rfThresh: threshold to go all out
        '''
        self.verbose = verbose
        self.impact = impact


    # this method should create a RTLearner, and train it for trading
    def addEvidence(self, symbol = "IBM", \
        sd=dt.datetime(2008,1,1), \
        ed=dt.datetime(2009,1,1), \
        sv = 10000):
        return None #not implemented

    def genStats(self, price, volume):
        '''
        Generates X and Y for data
        '''
        # prices_all["Y"] = Y
        changeVol = (volume.iloc[0] - volume) / volume.iloc[0]

        dr = (price.shift(-1)) / price - 1 #return for 1 day in future if you invested today
        prices = pd.DataFrame(price)
        prices['dr'] = dr * 50 + 300
        # ut.plot_data(prices)

        # print  "dr", dr.mean()
        dr = dr.fillna(method='bfill').fillna(method="ffill")
        # Y = dr.apply(lambda x: 1 if x > self.ybuy else -1 if x < -self.ybuy else 0) #predict future dr from past!
        Y = (dr - dr.min()) / (dr.max() - dr.min()) * 2 - 1
        momentum = (dr.shift(1) - dr) / dr
        momentum = momentum.fillna(method="bfill").fillna(method="ffill")

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

        # here we build a fake set of trades
        # your code should return the same sort of data
        dates = pd.date_range(sd, ed)
        prices_all = ut.get_data([symbol], dates)  # automatically adds SPY
        volumes_all = ut.get_data([symbol], dates, colname = "Volume")
        X, Y = self.genStats(prices_all[symbol], volumes_all[symbol])
        Ypred = self.learner.query(X)
        Ypred = Y
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

        if self.verbose: print(type(trades)) # it better be a DataFrame!
        if self.verbose: print(trades)
        if self.verbose: print(prices_all)
        if self.verbose: print(trades.sum().sum())
        return trades

if __name__=="__main__":
    print("One does not simply think up a strategy")

    sl = StrategyLearner()
    sv = 100000
    sl.addEvidence(symbol="ML4T-220",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
    trades = sl.testPolicy(symbol="ML4T-220",sd=dt.datetime(2010,1,1),ed=dt.datetime(2011,12,31),sv=100000)
    print(marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv).iloc[-1])
