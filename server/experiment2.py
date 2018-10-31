import marketsimcode
import StrategyLearner
import pandas as pd
from StrategyLearner import StrategyLearner
import datetime as dt
import util
import matplotlib.pyplot as plt
import numpy as np

#Rolling Mean
#

def startNorm(series):
    return (series - series.mean())/ series.std()

print "No impact"
syms = ["JPM"]
sl = StrategyLearner()
sv = 100000
sl.addEvidence(symbol="JPM",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
trades = sl.testPolicy(symbol="JPM",sd=dt.datetime(2010,1,1),ed=dt.datetime(2011,12,31),sv=100000)
# print(trades)
df = marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv)
plt.plot(df)
print "cummulative Return", df.iloc[-1] / df.iloc[0]
print "standard deviation", df.std()

print "Impact = .005"
sl = StrategyLearner(impact=0.005)
sv = 100000
sl.addEvidence(symbol="JPM",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
trades = sl.testPolicy(symbol="JPM",sd=dt.datetime(2010,1,1),ed=dt.datetime(2011,12,31),sv=100000)
df = marketsimcode.compute_portvals(trades, commission=0, impact=0.005, start_val=sv)
plt.plot(df)
print "cummulative Return", df.iloc[-1] / df.iloc[0]
print "standard deviation", df.std()

print "Impact = .001"
sl = StrategyLearner(impact=0.001)
sv = 100000
sl.addEvidence(symbol="JPM",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
trades = sl.testPolicy(symbol="JPM",sd=dt.datetime(2010,1,1),ed=dt.datetime(2011,12,31),sv=100000)
df = marketsimcode.compute_portvals(trades, commission=0, impact=0.001, start_val=sv)
plt.plot(df)
plt.title("Experiment 2")
plt.ylabel("Portfolio Value")
plt.xlabel("Date")
plt.legend(["Impact = 0", "Impact = 0.005", "Impact = 0.001"])
plt.show()
print "cummulative Return", df.iloc[-1] / df.iloc[0]
print "standard deviation", df.std()
