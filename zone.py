# -*- coding: utf-8 -*-
# zone.py

import numpy as np
import matplotlib.pyplot as plt

class Solution(object):
    def random(self, nX, nY, m):
        # m - number of companies
        self.zone_ctr = []
        for i in np.arange(0, m):
            ctr = np.random.uniform(low=0, high=nX, size=(1, m)).tolist()
            self.zone_ctr.append(ctr[0])
#        self.assignment = np.random.randint(low=0, high=m, size=((nX / 10), (nY / 10)))
        self.nCompanies = m
        self.fCost = None
    
    def solve(self, cost, priority, capability, ctr):
        assignment = [[None] * len(cost[0])] * len(cost)
        print(self.zone_ctr)
        for i in np.arange(0, 3):
            for x in np.arange(0, len(cost)):
                for y in np.arange(0, len(cost[x])):
                    sector_cost = [None, None]
                    for z in np.arange(0, self.nCompanies):
                        ratio = cost[x][y] / priority[x][y]
                        dist = np.sqrt((self.zone_ctr[z][0] - ctr[x][y][0])**2 + (self.zone_ctr[z][1] - ctr[x][y][1])**2)
                        sector_cost[z] = ratio * dist
                    z = np.argmin(sector_cost)
                    assignment[x][y] = z
            for z in np.arange(0, self.nCompanies):
                X = []
                Y = []
                for x in np.arange(0, len(cost)):
                    for y in np.arange(0, len(cost[0])):
                        if assignment[x][y] == z:
                            X.append(ctr[x][y][0])
                            Y.append(ctr[x][y][1])
                self.zone_ctr[z] = [np.mean(X), np.mean(Y)]
            print(self.zone_ctr)
            self.assignment = assignment
            
            X, Y = np.meshgrid(np.arange(0, len(cost)), np.arange(0, len(cost[0])))
            Z = assignment
            plt.figure()
            plt.contourf(X, Y, Z)
            plt.show()
    
#    def layer(self, nX, nY, m):
#        # m - number of companies
##        self.assignment = np.zeros(shape=(1, (int(nX) / 10) * (int(nY) / 10)))
#        assignment = np.zeros(shape=(int(nX) / 10, int(nY) / 10))
#        for x in np.arange(0, len(assignment)):
#            for y in np.arange(0, len(assignment[x])):
#                a = np.floor((y / len(assignment[x])) * m)
#                assignment[x][y] = int(a)
#        self.assignment = assignment.reshape((1, (int(nX) / 10) * (int(nY) / 10)))
#        self.assignment = self.assignment[0]
#        self.fCost = None
    
#    def create(self, assignment):
#        self.assignment = assignment
#        self.fCost = None
    
#    def mutate(self, m): # INCREASE MUTATION RATE RELATIVE TO DISTANCE FROM ZONE CENTRE?
#        for i in np.arange(0, len(self.assignment)):
#            random_sample = np.random.uniform()
#            if random_sample < 0.50:
#                self.assignment[i] = np.random.randint(low=0, high=m)
    
#    def flip(self, n, nX, nY, ctr):
#        genome = np.asarray(self.assignment)
#        assignment = genome.reshape((int(nX) / 10, int(nY) / 10))
#        for i in np.arange(0, n):
#            X = []
#            Y = []
#            for x in np.arange(0, len(assignment)):
#                for y in np.arange(0, len(assignment[x])):
#                    if assignment[x][y] == i:
#                        X.append(ctr[x][y][0])
#                        Y.append(ctr[x][y][1])
#            mean_X = np.mean(X)
#            mean_Y = np.mean(Y)
#            dist = []
#            iX = []
#            iY = []
#            for x in np.arange(0, len(assignment)):
#                for y in np.arange(0, len(assignment[x])):
#                    if assignment[x][y] == i:
#                        dist.append(np.sqrt((X[i] - mean_X)**2 + (Y[i] - mean_Y)**2))
#                        iX.append(x)
#                        iY.append(y)
#            i = np.argmax(dist)
#            new = np.random.randint(low=0, high=n)
#            while new == i:
#                new = np.random.randint(low=0, high=n)
#            ii = (iX[i] * len(assignment[x])) + iY[i] + 1
#            self.assignment[ii] = new
    
#    def change(self, n, m):
#        i = np.random.randint(low=0, high=n)
#        new_assignment = self.assignment
#        new_assignment[i] = np.random.randint(low=0, high=m)
#        return new_assignment
    
#    def test(self, n, nX, nY, cost, priority, capability, ctr):
        # n - number of companies
#        genome = np.asarray(self.assignment)
#        assignment = genome.reshape((int(nX) / 10, int(nY) / 10))               # Depends on sector_size
#        count = [0] * n
#        cum_cost = [0] * n
#        cum_priority = [0] * n
#        for x in np.arange(0, len(assignment)):
#            for y in np.arange(0, len(assignment[x])):
#                c = int(assignment[x][y])
#                count[c] += 1
#                cum_cost[c] += cost[x][y]
#                cum_priority[c] += priority[x][y]
#        cost_per_cap = np.asarray(cum_cost) / np.asarray(capability)
#        priority_per_cap = np.asarray(cum_priority) / np.asarray(capability)
#        cum_dist = [0] * n
#        dist_var = [0] * n
#        for i in np.arange(0, n):
#            X = []
#            Y = []
#            for x in np.arange(0, len(assignment)):
#                for y in np.arange(0, len(assignment[x])):
#                    if assignment[x][y] == i:
#                        X.append(ctr[x][y][0])
#                        Y.append(ctr[x][y][1])
#            mean_X = np.mean(X)
#            mean_Y = np.mean(Y)
#            var_X = np.var(X)
#            var_Y = np.var(Y)
#            dist_var[i] = var_X + var_Y
#            for j in np.arange(0, len(X)):
##                cum_dist[i] += np.sqrt((X[j] - mean_X)**2 + (Y[j] - mean_Y)**2)
#                cum_dist[i] += (X[j] - mean_X)**2 + (Y[j] - mean_Y)**2
#        dist = np.var(np.asarray(cum_dist) / np.asarray(count))
#        dist = np.sum(dist_var)
#        print(dist)
#        var_cost_per_cap = np.var(cost_per_cap)
#        print(var_cost_per_cap)
#        var_priority_per_cap = np.var(priority_per_cap)
#        print(var_priority_per_cap)
#        self.fCost = np.asarray(dist) + np.asarray(var_cost_per_cap) + np.asarray(var_priority_per_cap)
#        return self.fCost
    
    def output(self, nX, nY):
        assignment = np.asarray(self.assignment)
        return assignment.reshape((int(nX) / 10, int(nY) / 10))

#class Population(object):
#    def __init__(self, n, m, size=20):
#        self.solution = []
#        for i in np.arange(0, size):
#            self.solution.append(Solution())
#            self.solution[-1].random(n, m)
#    
#    def generation(self, n, nX, nY, sector_cost, sector_priority, capability, ctr):
#        cost = []
#        for S in self.solution:
#            if S.fCost == None:
#                cost.append(S.test(n, nX, nY, sector_cost, sector_priority, capability, ctr))
#            else:
#                cost.append(S.fCost)
#        inverse_cost = 1 / np.asarray(cost)
#        cum_inverse_cost = [inverse_cost[0]]
#        for i in np.arange(1, len(inverse_cost)):
#            cum_inverse_cost.append(cum_inverse_cost[-1] + inverse_cost[i])
#        selection_weight = np.asarray(cum_inverse_cost) / cum_inverse_cost[-1]
#        for c in np.arange(0, 10):
#            parent = []
#            for i in np.arange(0, 2):
#                random_sample = np.random.uniform()
#                found = False
#                i = 0
#                if random_sample < selection_weight[0]:
#                    found = True
#                else:
#                    while found == False:
#                        i += 1
#                        if random_sample > selection_weight[i-1]:
#                            if random_sample < selection_weight[i]:
#                                found = True
#                parent.append(self.solution[i])
#            iCrossover = np.random.randint(1, (int(nX) / 10) * (int(nY) / 10))
#            assignment = []
#            for a in np.arange(0, len(self.solution[0].assignment)):
#                if a <= iCrossover:
#                    assignment.append(parent[0].assignment[a])
#                else:
#                    assignment.append(parent[1].assignment[a])
#            self.solution.append(Solution())
#            self.solution[-1].create(assignment)
#            self.solution[-1].mutate(n)
#            cost.append(self.solution[-1].test(n, nX, nY, sector_cost, sector_priority, capability, ctr))
#            for i in np.arange(0, 10): # Number of sectors to flip
#                S.flip(n, nX, nY, ctr)
#        for i in np.arange(0, 10): # Number to purge
#            i = np.argmax(cost)
#            cost.pop(i)
#            self.solution.pop(i)
#    
#    def select_best(self, n, nX, nY, sector_cost, sector_priority, capability, ctr):
#        cost = []
#        for S in self.solution:
#            if S.fCost == None:
#                cost.append(S.test(n, nX, nY, sector_cost, sector_priority, capability, ctr))
#            else:
#                cost.append(S.fCost)
#        i = np.argmin(cost)
#        best = np.asarray(self.solution[i].assignment)
#        return best.reshape((int(nX) / 10, int(nY) / 10))
#    
#    def best_cost(self, n, nX, nY, sector_cost, sector_priority, capability, ctr):
#        cost = []
#        for S in self.solution:
#            if S.fCost == None:
#                cost.append(S.test(n, nX, nY, sector_cost, sector_priority, capability, ctr))
#            else:
#                cost.append(S.fCost)
#        i = np.argmin(cost)
#        best = self.solution[i].fCost
#        return best