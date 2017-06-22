# -*- coding: utf-8 -*-
"""
One-Sided Advance/Retreat Model
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters
base_FreeToEngaged = 0.10
base_AdvanceToEngaged = 0.25
base_EngagedToDead = 0.20
base_EngagedToFree = 0.75

class Unit(object):
    
    def __init__(self, path):
        self.path = path
        self.pos = 0
        self.stance = 'FREE'
        self.cover = np.random.uniform()
    
    def advance(self):
        self.pos += 1
        self.cover = np.random.uniform()
        # 25% chance that the unit becomes engaged when advancing
        if np.random.uniform() < base_AdvanceToEngaged:
            self.stance = 'FREE'
        # 75% chance that the unit advances freely
        else:
            self.stance = 'ENGAGED'
    
    def retreat(self):
        self.pos -= 1
        self.stance = 'FREE'
    
    def tick(self):
        if self.stance == 'FREE':
            if np.random.uniform() < base_FreeToEngaged:
                self.stance = 'ENGAGED'
        elif self.stance == 'ENGAGED':
            r = np.random.uniform()
            if r < base_EngagedToDead * (1 - self.cover):
                self.stance = 'DEAD'
            elif r > base_EngagedToFree:
                self.stance = 'FREE'

class Commander(object):
    
    def __init__(self, team, n, adv, ret):
        self.team = team
        self.adv = adv
        self.ret = ret
        self.score = 0
        self.unit = {}
        for a in np.arange(0, n):
            self.unit[a] = Unit(a)
            
    def getPositions(self):
        p = []
        for a in np.arange(0, len(self.unit)):
            p.append(self.unit[a].pos)
        return [p]
    
    def getCover(self):
        c = []
        for a in np.arange(0, len(self.unit)):
            c.append(self.unit[a].cover)
        return [c]
    
    def getStance(self):
        st = []
        for a in np.arange(0, len(self.unit)):
            st.append(self.unit[a].stance)
        return [st]
    
    def giveOrders(self):
        for a in np.arange(0, len(self.unit)):
            if self.unit[a].stance == 'FREE':
                if np.random.uniform() < self.adv * (1 - self.unit[a].cover):
                    self.unit[a].advance()
                    self.score += 1
            elif self.unit[a].stance == 'ENGAGED':
                if np.random.uniform() < self.ret * (1 - self.unit[a].cover):
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

def run(sol, n):
    commander = Commander(0, 10, sol[0], sol[1])
    s = []
    for t in np.arange(0, n):
        s.append(commander.score)
        commander.giveOrders()
    plotScore(s)
    return [commander.score]

def runIterations(sol, n):
    s_end = []
    for i in np.arange(0, n):
        print(i)
        s_end.append(run(sol, 100))
    return [np.mean(s_end)]

def runTrials(n):
    sol = [np.random.uniform(), np.random.uniform()]
    score = runIterations(sol, 20)
    for tr in np.arange(1, n):
        new_sol = [np.random.uniform(), np.random.uniform()]
        new_score = runIterations(new_sol, 20)
        if new_score > score:
            sol = new_sol
            score = new_score
    return [sol, score]
        

time = np.arange(0, 101)
iteration = np.arange(0, 16)
trial = np.arange(1, 6)

# Initial solution [adv, ret]
sol = [np.random.uniform(), np.random.uniform()]

commander = Commander(0, 10, sol[0], sol[1])
print(runTrials(10))