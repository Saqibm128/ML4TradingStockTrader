from flask import Flask, request
import marketsimcode
import StrategyLearner
import pandas as pd
from StrategyLearner import StrategyLearner
import datetime as dt
import util
import matplotlib.pyplot as plt
import numpy as np


app = Flask(__name__)

@app.route('/health')
def health():
    return "OK"

@app.route('/getStockActions')
def stockAction():
    stockName = request.json['stock']
    startTime = request.json['start_time']
    endTime = request.json['end_time']

    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()
