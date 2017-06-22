# -*- coding: utf-8 -*-
"""
One-Sided Advance/Retreat Model
"""

import numpy as np
import matplotlib.pyplot as plt

class Unit(object):
    
    def __init__(self, path):
        self.path = path
        self.pos = 0
        self.stance = 'FREE'
        self.cover = np.random.uniform()
    
    def advance(self):
        self.pos += 1
        self.cover = np.random.uniform()
        if np.random.uniform() < 0.25:
            self.stance = 'FREE'
        else:
            self.stance = 'ENGAGED'
    
    def retreat(self):
        self.pos -= 1
        self.stance = 'FREE'
    
    def tick(self):
        if self.stance == 'ENGAGED':
            r = np.random.uniform()
            if r < 0.25:
                self.stance = 'DEAD'
            elif r > 0.75:
                self.stance = 'FREE'

class Commander(object):
    
    def __init__(self, team, n):
        self.team = team
        self.adv = 0.50
        self.ret = 0.25
        self.score = 0
        self.unit = {}
        for a in np.arange(0, n):
            self.unit[a] = Unit(a)
            
    def getPositions(self):
        p = []
        for a in np.arange(0, len(self.unit)):
            p.append(self.unit[a].pos)
        return [p]
    
    def giveOrders(self):
        for a in np.arange(0, len(self.unit)):
            if self.unit[a].stance == 'FREE':
                if np.random.uniform() < self.adv:
                    self.unit[a].advance()
                    self.score += 1
            elif self.unit[a].stance == 'ENGAGED':
                if np.random.uniform() < self.ret:
                    self.unit[a].retreat()
                    self.score -= 1
            self.unit[a].tick()

def plotPositions(p):
    plt.figure()
    pos = plt.scatter(np.arange(0, len(commander.unit)), p)
    plt.show()

def plotScore(s):
    plt.figure()
    score = plt.plot(s)
    plt.show()
                    
commander = Commander(0, 10)

clock = np.arange(0, 10)
p = commander.getPositions()
plotPositions(p)
s = []
for t in clock:
    s.append(commander.score)
    commander.giveOrders()
    p = commander.getPositions()
    plotPositions(p)
plotScore(s)