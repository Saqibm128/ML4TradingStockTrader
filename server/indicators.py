import pandas as pd
import StrategyLearner as strat
import util
import matplotlib.pyplot as plt
import numpy as np

#Rolling Mean
#

def startNorm(series):
    return (series - series.mean())/ series.std()

syms = ["JPM"]
dates = pd.date_range("01/01/2009", "01/01/2010")

data = util.get_data(syms, dates)
volume = util.get_data(syms, dates, colname = "Volume")["JPM"]  # automatically adds SPY


JPM = data["JPM"]
ax = (JPM).plot()
JPMStd = JPM.rolling(5).std().fillna(method="ffill").fillna(method="bfill").astype(np.float)
plt.fill_between(JPM.index, \
                 (JPM - JPMStd).values, \
                 (JPM + JPMStd).values, \
                 color='Blue', alpha=.5)
plt.title("JP Morgan Stock, 2009 vs Rolling Mean")
plt.plot((JPM.rolling(5).mean().fillna(method="bfill")))
plt.xlabel("Time")
plt.ylabel("Price")
plt.legend(["True Price and Bollinger Bands (+- 1 stdev)", "Rolling Mean"])

plt.show()
plt.gcf().clear()

# Rolling Standard Deviation
#

JPM = data["JPM"]
ax = startNorm(JPM).plot()
JPMStd = JPM.rolling(5).std().fillna(method="ffill").fillna(method="bfill").astype(np.float)
plt.fill_between(JPM.index, \
                 startNorm(JPM - JPMStd).values, \
                 startNorm(JPM + JPMStd).values, \
                 color='Blue', alpha=.5)
plt.title("Normalized JP Morgan Stock vs Normalized Rolling St. Dev., 2009")
plt.plot(startNorm(JPM.rolling(5).std().fillna(method="bfill")))
plt.xlabel("Time")
plt.ylabel("Normalized Value")
plt.legend(["True Price and Bollinger Bands (+- 1 stdev)", "Price St. Dev."])
plt.show()
plt.gcf().clear()

# Rolling Z-Score
#

JPM = data["JPM"]
ax = startNorm(JPM.rolling(5).mean().fillna(method="ffill").fillna(method="bfill")).plot()
JPMStd = JPM.rolling(5).std().fillna(method="ffill").fillna(method="bfill").astype(np.float)
plt.plot(startNorm(JPMStd))
plt.plot((JPM - JPM.rolling(5).mean().fillna(method="ffill")).fillna(method="bfill") / JPMStd)
# plt.fill_between(JPM.index, \
#                  startNorm(JPM - JPMStd).values, \
#                  startNorm(JPM + JPMStd).values, \
#                  color='Blue', alpha=.5)
plt.title("Normalized JP Morgan Stock vs Normalized Rolling Z-Score, 2009")
# plt.plot(startNorm(JPM.rolling(5).std().fillna(method="bfill")))
plt.xlabel("Time")
plt.ylabel("Normalized Value")
plt.legend(["Rolling Mean", "Rolling Standard Deviation", "Rolling Z-Score"])
plt.show()
plt.gcf().clear()

# Rolling Volume Stdev
#
JPM = data["JPM"]
ax = startNorm(JPM).plot()
JPMStd = JPM.rolling(5).std().fillna(method="ffill").fillna(method="bfill").astype(np.float)
plt.fill_between(JPM.index, \
                 startNorm(JPM - JPMStd).values, \
                 startNorm(JPM + JPMStd).values, \
                 color='Blue', alpha=.5)
plt.title("Normalized JP Morgan Stock vs Normalized Rolling Volume St. Dev., 2009")
plt.plot(startNorm(volume.rolling(5).std().fillna(method="bfill")))
plt.xlabel("Time")
plt.ylabel("Normalized Value")
plt.legend(["True Price and Bollinger Bands (+- 1 stdev)", "Rolling Volume St. Dev."])
plt.show()
plt.gcf().clear()

# Volume Daily Change
#
changeVol = (volume.iloc[0] - volume) / volume.iloc[0]
JPM = data["JPM"]
ax = startNorm(JPM).plot()
JPMStd = JPM.rolling(5).std().fillna(method="ffill").fillna(method="bfill").astype(np.float)
plt.fill_between(JPM.index, \
                 startNorm(JPM - JPMStd).values, \
                 startNorm(JPM + JPMStd).values, \
                 color='Blue', alpha=.5)
plt.title("Normalized JP Morgan Stock vs Change In Volume (Daily), 2009")
plt.plot(startNorm(changeVol))
plt.xlabel("Time")
plt.ylabel("Normalized Value")
plt.legend(["True Price and Bollinger Bands (+- 1 stdev)", "Change In Volume (Daily)"])
plt.show()
plt.gcf().clear()
