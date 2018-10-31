import numpy as np
import pandas as pd

class RTLearner:
    def __init__(self, leaf_size = 1, verbose=False):
        self.leaf_size = leaf_size
        self.verbose = verbose
        self.tree = np.ndarray(shape = [5, 0]) # isLeaf, factor, split val, left, right
        self.nextEmpty = 0 #current place that points to empty place on tree
    def author(self):
        return 'msaqib3'


    def addNode(self, node):

        if self.verbose and node[0] == True:
            print "Adding leaf: " + str(self.nextEmpty) + str(node)
        elif (self.verbose):
            print "Adding node " + str(self.nextEmpty) + str(node)
        self.tree = np.append(self.tree, node);
        self.nextEmpty += 1
        self.tree = self.tree.reshape([self.nextEmpty, 5])

    def addEvidence(self, Xtrain, Ytrain):
        if self.verbose:
            print "adding evidence"
        if Xtrain.shape[0] <= self.leaf_size:
            self.addNode([True, np.nan, np.median(Ytrain), np.nan, np.nan])
            return;
        elif (Ytrain == Ytrain[0]).all(): #all same nodes
            self.addNode([True, np.nan, np.median(Ytrain), np.nan, np.nan])
            return;
        else:
            maxInd = np.random.randint(Xtrain.shape[1])
            splitVal = np.median(Xtrain[:,maxInd])
            leftXtrain = Xtrain[Xtrain[:, maxInd] < splitVal]
            leftYtrain = Ytrain[Xtrain[:, maxInd] < splitVal]
            rightXtrain = Xtrain[Xtrain[:, maxInd] >= splitVal]
            rightYtrain = Ytrain[Xtrain[:, maxInd] >= splitVal]
            if leftXtrain.shape[0] == 0 or rightXtrain.shape[0] == 0:
                self.addNode([True, np.nan, np.median(Ytrain), np.nan, np.nan])
                return;
            locationOfNode = self.nextEmpty
            self.addNode([False, maxInd, splitVal, self.nextEmpty + 1, np.nan]) #will figure out right node after left node finishes
            self.addEvidence(leftXtrain, leftYtrain)
            self.tree[locationOfNode, 4] = self.nextEmpty
            self.addEvidence(rightXtrain, rightYtrain)

    def query(self, Xtest):
        Ytest = np.ndarray(shape = [Xtest.shape[0]])
        for i in range(Xtest.shape[0]):
            Ytest[i] = self.traverse(Xtest[i])
        return Ytest

    def traverse(self, X, node = 0):
        currentNode = self.tree[node]
        if currentNode[0] == True:
            return currentNode[2]
        if X[int(currentNode[1])] >= currentNode[2]:
            return self.traverse(X, int(currentNode[4]))
        else:
            return self.traverse(X, int(currentNode[3]))
