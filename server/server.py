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
    learnStartTime = request.json['learn_start_time'] #epoch times
    learnEndTime = request.json['learn_end_time']

    applyStartTime = request.json['apply_start_time']
    applyEndTime = request.json['apply_start_time']


    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()
