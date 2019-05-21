import pandas as pd


# use the flat files first to avoid getting charged when messing around here
def get_data(symbols, date_range=pd.date_range("1/1/2018", "1/1/2019"), colname = "Adj Close", addSPY=True, imputeMethod="keep"):
    toReturn = pd.DataFrame()
    if addSPY and "SPY" not in symbols:
        symbols.append("SPY")
    for symbol in symbols:
        data = pd.read_csv("data/" + symbol + ".csv", index_col=0).dropna()
        data.index = pd.to_datetime(data.index)
        toReturn[symbol] = data[colname][date_range]
        if imputeMethod == "keep": #We don't drop the bad indices (i.e. weekends) and assume continuous
            toReturn[symbol] = toReturn[symbol].fillna(method='ffill').fillna(method='bfill')
        else:
            toReturn[symbol] = toReturn[symbol].dropna() #query price during weekends,etc. shouldn't happen normally?
    return toReturn
