import pandas as pd
#use the flat files first to avoid getting charged when messing around here
def get_data(symbols, date_range=pd.date_range("1/1/2018", "1/1/2019"), colname = "Open", addSPY=True):
    toReturn = pd.DataFrame()
    if addSPY:
        symbols.append("SPY")
    for symbol in symbols:
        data = pd.read_csv("data/" + symbol + ".csv", index_col=0).dropna()
        data.index = pd.to_datetime(data.index)
        toReturn[symbol] = data[colname][date_range].dropna()
    return toReturn
