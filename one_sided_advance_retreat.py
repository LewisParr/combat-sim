# -*- coding: utf-8 -*-
"""
One-Sided Advance/Retreat Model
"""

import numpy as np
import matplotlib.pyplot as plt

# Parameters
base_FreeToEngaged = 0.10
base_AdvanceToEngaged = 0.25
base_TakeCasualty = 0.20
base_EngagedToFree = 0.20
max_cover = 0.95
base_fort = 0.05
base_support_bonus = 0.15
base_DeadConcede = 0.50
base_EngagedStressInc = 0.04
base_FreeStressInc = 0.02
base_CasStressInc = 0.12
base_RetreatStressInc = 0.08

class Unit(object):
    
    def __init__(self, path):
        self.path = path
        self.pos = 0
        self.stance = 'FREE'
        self.max_cover = max_cover
        self.cover = np.random.uniform(0, self.max_cover)
        self.fort = base_fort
        self.moved = False
        self.members = 10
        self.max_members = 10
        self.stress = 0
    
    def advance(self):
        self.pos += 1
        self.cover = np.random.uniform(0, self.max_cover)
        # 25% chance that the unit becomes engaged when advancing
        if np.random.uniform() < base_AdvanceToEngaged:
            self.stance = 'FREE'
        # 75% chance that the unit advances freely
        else:
            self.stance = 'ENGAGED'
        self.moved = True
    
    def retreat(self):
        self.pos -= 1
        self.stress -= base_RetreatStressInc
        self.stance = 'FREE'
        self.moved = False
    
    def withdraw(self, commander):
        self.pos -= 1
        self.stance = 'WITHDRAWN'
        commander.unitDeath(self.path)
    
    def tick(self, commander):
        if self.stance == 'FREE':
            self.stress -= base_FreeStressInc
            if self.stance != 'DEAD':
                if np.random.uniform() < base_FreeToEngaged:
                    self.stance = 'ENGAGED'
        elif self.stance == 'ENGAGED':
            self.stress += base_EngagedStressInc
            nSupporting = commander.getAdjacentFree(self.path)[0]
            adj_cover = self.cover + (nSupporting * base_support_bonus)
            if adj_cover >= 1:
                adj_cover = 0.99
            if np.random.uniform() < base_TakeCasualty * (1 - adj_cover) * (self.max_members / self.members) + self.stress:
                self.members -= 1
                self.stress += base_CasStressInc
                if self.members <= 0:
                    self.stance = 'DEAD'
                    commander.unitDeath(self.path)
            adj_EngagedToFree = base_EngagedToFree + (nSupporting * base_support_bonus)
            if np.random.uniform() < adj_EngagedToFree * (self.members / self.max_members) - self.stress:
                self.stance = 'FREE'
                commander.kills += 1
        elif self.stance == 'DEAD':
            if np.random.uniform() < base_DeadConcede:
                self.pos -= 1
                commander.score -= 1
        if self.moved == False:
            self.cover += self.fort
            if self.cover > self.max_cover:
                self.cover = self.max_cover
        self.moved = False

class Commander(object):
    
    def __init__(self, team, n, r, adv, ret, wit):
        self.team = team
        self.adv = adv
        self.ret = ret
        self.wit = wit
        self.sup = 0.5
        self.score = 0
        self.unit = {}
        for a in np.arange(0, n):
            self.unit[a] = Unit(a)
        self.rein = r
        self.nRet = 0
        self.kills = 0
        self.withdrawnMembers = 0
            
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
    
    def getAdjacentFree(self, path):
        adj = []
        if path > 0:
            adj.append(path - 1)
        if path < len(self.unit) - 1:
            adj.append(path + 1)
        count = 0
        for a in adj:
            if self.unit[a].pos == self.unit[path].pos:
                if self.unit[a].stance == 'FREE':
                    count += 1 * (self.unit[a].members / self.unit[a].max_members)
        return [count]
    
    def getFreeNeighbours(self, path):
        adj = np.array([])
        if path > 0:
            adj = np.append(adj, path - 1)
        if path < len(self.unit) - 1:
            adj = np.append(adj, path + 1)
        free = np.array([False]*len(adj))
        for a in adj:
            if self.unit[a].stance == 'FREE':
                free[np.where(adj == a)] = True
        adj = adj[free].tolist()
        return [adj]
    
    def getSurviving(self):
        count = 0
        for a in np.arange(0, len(self.unit)):
            if self.unit[a].stance != 'DEAD':
                count += self.unit[a].members
        return [count + (self.rein * 10) + self.withdrawnMembers]
    
    def unitDeath(self, path):
        if self.rein > 0:
            self.unit[path].stance == 'ENGAGED'
            self.unit[path].members = self.unit[path].max_members
            self.rein -= 1
    
    def giveOrders(self):
        for a in np.arange(0, len(self.unit)):
            if self.unit[a].members < self.unit[a].max_members / 2:
                if np.random.uniform() < self.ret + 0.1 * ((self.unit[a].members / 2) - self.unit[a].members):
                    self.withdrawnMembers += self.unit[a].members
                    self.unit[a].withdraw(self)
            if self.unit[a].stance == 'FREE':
                if np.random.uniform() < self.adv * (1 - self.unit[a].cover) - self.unit[a].stress:
                    self.unit[a].advance()
                    self.score += 1
            elif self.unit[a].stance == 'ENGAGED':
                print(self.unit[a].members)
                print(self.unit[a].stance)
                if np.random.uniform() < self.ret * (1 - self.unit[a].cover) * (self.unit[a].max_members / self.unit[a].members) + self.unit[a].stress:
                    self.unit[a].retreat()
                    self.score -= 1
                    self.nRet += 1
                else:
                    free = self.getFreeNeighbours(a)[0]
                    if len(free) > 0:
                        for b in free:
                            if self.unit[b].pos < self.unit[a].pos:
                                if np.random.uniform() < 1 - self.unit[b].stress:
                                    self.unit[b].advance()
                                    self.score += 1
                            else:
                                if np.random.uniform() < 0.5 + self.unit[b].stress:
                                    self.unit[b].retreat()
                                    self.score -= 1
            self.unit[a].tick(self)

class Solution(object):
    
    def genRandom(self):
        self.sol = [np.random.uniform(), np.random.uniform(), np.random.uniform()]
    
    def getScore(self):
        [score, nd, nRet, nK] = runIterations(self, 20, 100)
        self.score = score
        self.nd = nd
        self.nRet = nRet
        self.nK = nK
    
    def crossover(self, parent1, parent2):
        self.sol = []
        slice_point = np.random.randint(0, 4)
        if slice_point == 0:
            self.sol = parent2.sol
        elif slice_point < 3:
            self.sol[0:slice_point] = parent1.sol[0:slice_point]
            self.sol[slice_point:4] = parent2.sol[slice_point:4]
        else:
            self.sol = parent1.sol
    
    def mutation(self):
        for n in np.arange(0, len(self.sol)):
            self.sol[n] = self.sol[n] + ((np.random.uniform() - 0.5) / 10)
        
    def genChild(self, parent1, parent2):
        self.crossover(parent1, parent2)
        self.mutation()
        
class Population(object):
    
    def __init__(self):
        self.solution = {}
        for n in np.arange(0, 10):
            self.solution[n] = Solution()
            self.solution[n].genRandom()
            self.solution[n].getScore()
    
    def getMinScore(self):
        s = []
        for n in np.arange(0, len(self.solution)):
            s.append(self.solution[n].score)
        return [np.min(s)]
    
    def outputBestSol(self):
        s = []
        for n in np.arange(0, len(self.solution)):
            s.append(self.solution[n].score)
        max_s = np.max(s)
        best_sol = s.index(max_s)
        return [self.solution[best_sol].sol, self.solution[best_sol].score, self.solution[best_sol].nd, self.solution[best_sol].nRet, self.solution[best_sol].nK]
    
    def randomSelection(self):
        selection = []
        for n in np.arange(0, 4):
            is_selected = True
            while is_selected == True:
                proposed_selection = np.random.randint(0, len(self.solution))
                is_selected = proposed_selection in selection
            selection.append(proposed_selection)
        return [selection]
    
    def weightedSelection(self, selection):
        s = []
        for n in selection:
            s.append(self.solution[n].score)
        adj_s = s - np.min(s) + 1
        adj_s = adj_s.tolist()
        prob = []
        for n in np.arange(0, len(adj_s)):
            prob.append(adj_s[n] / np.sum(adj_s))
        cum_prob = []
        for n in np.arange(0, len(prob)):
            cum_prob.append(np.sum(prob[0:n+1]))
        p_selection = []
        for n in np.arange(0, 2):
            is_selected = True
            while is_selected == True:
                proposed_parent = np.random.randint(0, len(selection))
                is_selected = proposed_parent in p_selection
            p_selection.append(proposed_parent)
        return [p_selection]
    
    def genChild(self):
        child = Solution()
        selection = self.randomSelection()[0]
        p_selection = self.weightedSelection(selection)[0]
        child.genChild(self.solution[selection[p_selection[0]]], self.solution[selection[p_selection[1]]])
        child.getScore()
        if child.score > self.getMinScore()[0]:
            self.solution[len(self.solution)] = child
            print('Child survived.')
        else: 
            print('Child died.')

def plotPositions(p):
    plt.figure()
    pos = plt.scatter(np.arange(0, len(commander.unit)), p)
    plt.show()

def plotScore(s):
    plt.figure()
    score = plt.plot(s)
    plt.show()

def run(solution, n):
    commander = Commander(0, 10, 4, solution.sol[0], solution.sol[1], solution.sol[2])
    s = []
    for t in np.arange(0, n):
        s.append(commander.score)
        commander.giveOrders()
    plotScore(s)
    return [commander.score, commander.getSurviving()[0], commander.nRet, commander.kills]

def runIterations(solution, nI, nR):
    s_end = []
    nd_end = []
    nRet_end = []
    nK_end = []
    for i in np.arange(0, nI):
        print(i)
        [s, nd, nRet, nK] = run(solution, nR)
        s_end.append(s)
        nd_end.append(nd)
        nRet_end.append(nRet)
        nK_end.append(nK)
    return [np.mean(s_end), np.mean(nd_end), np.mean(nRet_end), np.mean(nK_end)]

def extrapolate(score, nd):
    decay_const = - np.log10(nd / 140)
    s_per_m = score / nd
    survivors = []
    s = []
    s_cum = []
    for t in np.arange(0, 100):
        survivors.append(140 * np.exp(- decay_const * t))
        s.append(survivors[t] * s_per_m)
        s_cum.append(np.sum(s[0:t+1]))
    return [s_cum[len(s_cum)-1]]

# Generate initial population
pop = Population()

# Generate and test child solutions
for tr in np.arange(0, 10):
    pop.genChild()

# Extrapolate best solution into the future
[sol, score, nd, nRet, nK] = pop.outputBestSol()
proj_score = extrapolate(score, nd)[0]

# Output the best solution
print(pop.outputBestSol())
print(proj_score)