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

syms = ["JPM"]
sl = StrategyLearner()
sv = 100000
sl.addEvidence(symbol="JPM",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
trades = sl.testPolicy(symbol="JPM",sd=dt.datetime(2008,1,1),ed=dt.datetime(2009,12,31),sv=100000)
# print(trades)
df = marketsimcode.compute_portvals(trades, commission=0, impact=0, start_val=sv)
plt.plot(df)

dates = pd.date_range("01/01/2008", "12/31/2009")
benchmark = pd.DataFrame(index=dates, columns=["JPM"])
# print(benchmark)
benchmark["JPM"] = 0
benchmark.loc[benchmark.index[0], "JPM"] = 1000
benchmark.loc[benchmark.index[-1],"JPM"] = -1000
# print(pd.isnull(benchmark).any())
df = marketsimcode.compute_portvals(benchmark, commission=0, impact=0, start_val=sv)
plt.plot(df)
plt.title("Experiment 1")
plt.ylabel("Portfolio Value")
plt.xlabel("Date")
plt.legend(["StrategyLearner Portfolio", "Benchmark Portfolio"])
plt.show()
