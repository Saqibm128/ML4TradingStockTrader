import numpy as np
import pandas as pd

class BagLearner:
    def __init__(self, learner, kwargs={}, bags=20, boost=False, verbose=False):
        self.verbose = verbose
        self.bags = bags
        self.learners = []
        for bag in range(self.bags):
            self.learners.append(learner(**kwargs))
        self.boost = boost

    def author(self):
        return 'msaqib3'

    def addEvidence(self, Xtrain, Ytrain):
        for bag in range(self.bags):
            index = np.random.randint(low=0, high=Xtrain.shape[0], size=Xtrain.shape[0])
            self.learners[bag].addEvidence(Xtrain[index], Ytrain[index])

    def query(self, Xtest):
        results = np.ndarray([self.bags, Xtest.shape[0]])
        for bag in range(self.bags):
            results[bag] = self.learners[bag].query(Xtest)
        return results.mean(axis=0)
