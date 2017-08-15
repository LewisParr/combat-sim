# -*- coding: utf-8 -*-
# fuzzy.py

import numpy as np
import matplotlib.pyplot as plt

class Rule(object):
    def plot(self):
        print(self.name)
        for f in self.function:
            f.plot()
    
    def fireStrength(self, val):
        # val is [a, b] values to be used in membership functions
        i = 0
        strength = []
        for f in self.function:
            strength.append(f.fireStrength(val[i]))
            i += 1
        return strength

class AssetsKilled(Rule):
    def __init__(self, param, weight):
        # param is [[x1, x2], [x1, x2]] values used to build the membership functions
        self.name = 'Assets Killed Rule'
        self.function = [ManyEnemyAssetsKilled(param[0]), ManyFriendlyAssetsSurvive(param[1])]
        self.weight = weight

class BattlespaceInformation(Rule):
    def __init__(self, param, weight):
        # param is [x1, x2] values
        self.name = 'Battlespace Information Rule'
        self.function = [MuchBattlespaceVisible(param)]
        self.weight = weight
    
class MembershipFunction(object):
    def plot(self):
        plt.figure()
        plt.plot(self.X, self.Y)
        plt.xlabel(self.xlabel)
        plt.ylabel('Truth Value')
        plt.title(self.name)
        plt.show()
    
    def membershipFunction(self, param):
        # param is [x1, x2] values used to build the membership function
        X = np.linspace(0, 1, num=101)
        Y = []
        self.m = 1 / (param[1] - param[0])
        self.c = - param[0] / (param[1] - param[0])
        for x in X:
            if x < param[0]:
                Y.append(0)
            elif x <= param[1]:
                Y.append((self.m * x) + self.c)
            else:
                Y.append(1)
        self.X = X
        self.Y = Y
        self.param = param
        
    def fireStrength(val):
        if val < self.param[0]:
            return 0.0
        elif val <= self.param[1]:
            return (self.m * val) + self.c
        else:
            return 1.0

class ManyEnemyAssetsKilled(MembershipFunction):
    def __init__(self, param):
        self.name = 'Many Enemy Assets Killed'
        self.xlabel = 'Fraction of Enemy Assets Killed'
        self.membershipFunction(param)

class ManyFriendlyAssetsSurvive(MembershipFunction):
    def __init__(self, param):
        self.name = 'Many Friendly Assets Killed'
        self.xlabel = 'Fraction of Friendly Assets Survive'
        self.membershipFunction(param)

class MuchBattlespaceVisible(MembershipFunction):
    def __init__(self, param):
        self.name = 'Much of the Battlespace Visible'
        self.xlabel = 'Fraction of Battlespace Visible'
        self.membershipFunction(param)