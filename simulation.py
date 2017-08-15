# -*- coding: utf-8 -*-
# simulation.py

import genetic
import scenario
import environment
import commander
import event

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

np.random.seed(0)

class Optimise(object):
    def __init__(self, goal, nInitialSolutions, nGenerations):
        self.goal = goal
        self.nInitialSolutions = nInitialSolutions
        self.nGenerations = nGenerations
        self.create_Populations()
        self.solve()
        
    def create_Populations(self):
        self.pop = []
        for i in np.arange(0, 2):
            self.pop.append(genetic.Population(self.nInitialSolutions))
    
    def solve(self):
        for g in np.arange(0, self.nGenerations):                               # Repeat process for given number of generations
            if g != 0:                                                          # Generate a new environment and scenario if optimising globally and this is not the first generation
                if self.goal == 'GLOBAL':
#                    self.env = generate_Environment()
                    scene = scenario.TestScenario()
            else:
                self.env = generate_Environment()
                scene = scenario.TestScenario()
            selected = []                                                       # Select solutions for simulation in this generation
            for i in np.arange(0, 2):
                selected.append(self.pop[i].chooseSolutions())
            for a in np.arange(0, len(selected[0])):                            # Simulate each solution pair
                self.force = []                                                 # Initialise commanders
                self.force.append(commander.EnemyCommander(0, selected[0][a].parameters))
                self.force.append(commander.FriendlyCommander(1, selected[1][a].parameters))
                self.force[0].assignObjective(scene.adversary_objective)
                self.force[0].assignAssets(scene.adversary_assets)
                self.force[0].assignAssetLocations(scene.adversary_asset_locations, scene.adversary_fob_location)
                self.force[1].assignObjective(scene.friendly_objective)
                self.force[1].assignAssets(scene.friendly_assets)
                self.force[1].assignAssetLocations(scene.friendly_asset_locations, scene.friendly_fob_location)
                plot_Locations(self.env, self.force)                            # Plot asset locations
                for F in self.force:                                            # Decompose mission objective
                    F.decomposeObjective(F.objective, self.env)
                    print('Number of objectives: %s' % nx.number_of_nodes(F.obj_graph))
                    print('Number of dependecies: %s' % nx.number_of_edges(F.obj_graph))
                for t in np.arange(1, 51):                                      # Step through time
                    print('Timestep: %s' % t)
                    self.timestep()                                             # Perform timestep operations
                    if np.mod(t, 100) == 0:
                        plot_Locations(self.env, self.force)
                        plot_Detected(self.env, self.force)
                self.end_simulation()
                # Output results
                plot_Attrition_Rates(self.force)
                plot_Number_Active(self.force)
                plot_Visible_Area(self.force)
                plot_Number_Detected(self.force)
                # Assess solution fitness
                adversary_assets_survived = self.force[0].active_assets[-1] / self.force[0].active_assets[0]
                friendly_assets_survived = self.force[1].active_assets[-1] / self.force[1].active_assets[0]
                adversary_assets_killed = 1 - friendly_assets_survived
                friendly_assets_killed = 1 - adversary_assets_survived
                adversary_battlespace_visibility = np.mean(self.force[0].visible_area)
                friendly_battlespace_visibility = np.mean(self.force[0].visible_area)
                self.pop[0].receive_Simulation_Result(a, [adversary_assets_killed, adversary_assets_survived], adversary_battlespace_visibility)
                self.pop[1].receive_Simulation_Result(a, [friendly_assets_killed, friendly_assets_survived], friendly_battlespace_visibility)
            if g < self.nGenerations-1:
                for p in self.pop:                                              # Breed populations
                    p.breed()
            else:
                self.end_solve()
    
    def timestep(self):
        # Detection
        for F in self.force:
            F.detect(self.env, self.force[F.enemy_forceID])
        # Assess objective states
        for F in self.force:
            F.updateObjectiveStatus(self.env, self.force[F.enemy_forceID].hq.member.location)
        # Give orders
        for F in self.force:
            F.giveOrders(self.env)
        # Event creation
        event_queue = []
        for F in self.force:
            [forceID, companyID, platoonID, sectionID, manID, eventType, eventData] = F.createEvents(self.env, self.force[F.enemy_forceID])
            for a in np.arange(0, len(forceID)):
                for b in np.arange(0, len(companyID[a])):
                    for c in np.arange(0, len(platoonID[a][b])):
                        for d in np.arange(0, len(sectionID[a][b][c])):
                            if eventType[a][b][c][d] == 'MOVE':
                                source = [forceID[a], companyID[a][b], platoonID[a][b][c], sectionID[a][b][c][d], manID[a][b][c][d]]
                                event_queue.append(event.MovementEvent(source, eventData[a][b][c][d]))
                            if eventType[a][b][c][d] == 'FIRE':
                                source = [forceID[a], companyID[a][b], platoonID[a][b][c], sectionID[a][b][c][d], manID[a][b][c][d]]
                                target = eventData[a][b][c][d][0]
                                event_queue.append(event.FireEvent(source, target, eventData[a][b][c][d][1], eventData[a][b][c][d][2]))
        # Event effect calculation
        for E in event_queue:
            if E.type == 'MOVE':
                pass
            elif E.type == 'FIRE':
                E.calculate()
        # Event result application
        for E in event_queue:
            if E.type == 'MOVE':
                E.apply(self.force)
            elif E.type == 'FIRE':
                E.apply(self.force)
        # Find number of surviving assets
        count = []
        for F in self.force:
            count.append(F.countActive())
        print('Surviving Assets: %s' % count)
        # Record the state of each force
        for F in self.force:
            F.record(self.env)

    def end_simulation(self):
        for F in self.force:
            F.end_simulation()
    
    def end_solve(self):
        # Plot evolution of the mean fitness
        plt.figure()
        c = ['r', 'b']
        for i in np.arange(0, 2):
            plt.plot(self.pop[i].mean_fitness, c=c[i])
        plt.xlabel('Generation')
        plt.ylabel('Mean Fitness')
        plt.title('Mean Fitness of Tested Solutions')
        plt.show()

def generate_Environment():
    env = environment.Environment(260, 260)
    env.genTerrain(1)
#    env.saveElevationData()
#    env.loadElevationData()
    env.plotElevation()
    env.buildVisibilityMaps()
#    env.saveVisibilityMaps()
#    env.loadVisibilityMaps()
    return env

def plot_Locations(env, force):
    X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
    Z = env.getTerrainCellElevations()
    plt.figure()
    plt.contourf(X, Y, Z)
    c = ['r', 'b']
    a = 0
    for F in force:
        x = []
        y = []
        for C in np.arange(0, len(F.company)):
            for P in np.arange(0, len(F.company[C].platoon)):
                for S in np.arange(0, len(F.company[C].platoon[P].section)):
                    for M in np.arange(0, len(F.company[C].platoon[P].section[S].unit.member)):
                        if F.company[C].platoon[P].section[S].unit.member[M].status != 2:
                            x.append(F.company[C].platoon[P].section[S].unit.member[M].location[0])
                            y.append(F.company[C].platoon[P].section[S].unit.member[M].location[1])
        plt.scatter(x, y, c=c[a], marker='.')
        plt.scatter(F.hq.member.location[0], F.hq.member.location[1], c=c[a], marker='x')
        a += 1
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Asset Location')
    plt.show()

def plot_Detected(env, force):
    X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
    Z = env.getTerrainCellElevations()
    plt.figure()
    plt.contourf(X, Y, Z)
    c = ['b', 'r'] # Colours are reversed (locations represent adversary)
    a = 0
    for F in force:
        x = []
        y = []
        for l in F.detected_location:
            x.append(l[0])
            y.append(l[1])
        plt.scatter(x, y, c=c[a], marker='.')
        a += 1
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Detected Enemy Asset Location')
    plt.show()

def plot_Number_Active(force):
    plt.figure()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.plot(F.active_assets, c=c[a])
        a += 1
    plt.xlabel('Timestep')
    plt.ylabel('Active Assets')
    plt.title('Number of Active Assets')

def plot_Attrition_Rates(force):
    plt.figure()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.plot(F.calculateAttritionRate, c=c[a])
        a += 1
    plt.xlabel('Timestep')
    plt.ylabel('Attrition Rate')
    plt.title('Force Attrition Rates')

def plot_Visible_Area(force):
    plt.figure()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.plot(F.visible_area, c=c[a])
        a += 1
    plt.xlabel('Timestep')
    plt.ylabel('Visible Area')
    plt.title('Fraction of Environment Visible')
    
def plot_Number_Detected(force):
    plt.figure()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.plot(F.detected_enemy_assets, c=c[a])
        a += 1
    plt.xlabel('Timestep')
    plt.ylabel('Enemy Assets')
    plt.title('Number of Detected Enemy Assets')

test = Optimise('GLOBAL', 3, 2)

# Create graph of enemy assets
#E = nx.DiGraph()
#color_map = []
#E.add_node(force[0])
#color_map.append('red')
#for C in force[0].company:
#    E.add_node(C)
#    color_map.append('orange')
#    E.add_edge(force[0],C)
#    for P in C.platoon:
#        E.add_node(P)
#        color_map.append('yellow')
#        E.add_edge(C,P)
#        for S in P.section:
#            E.add_node(S)
#            color_map.append('green')
#            E.add_edge(P,S)

# Draw graph of enemy assets
#plt.figure()
#plt.title('Enemy Assets')
#nx.draw(E, node_color=color_map)
#plt.show()

# Create graph of friendly assets
#F = nx.DiGraph()
#color_map = []
#F.add_node(force[1])
#color_map.append('red')
#for C in force[1].company:
#    F.add_node(C)
#    color_map.append('orange')
#    F.add_edge(force[1],C)
#    for P in C.platoon:
#        F.add_node(P)
#        color_map.append('yellow')
#        F.add_edge(C,P)
#        for S in P.section:
#            F.add_node(S)
#            color_map.append('green')
#            F.add_edge(P,S)

# Draw graph of friendly assets
#plt.figure()
#plt.title('Friendly Assets')
#nx.draw(F, node_color=color_map)
#plt.show()

# Assign assets to objectives
#for F in force:
#    F.assignAssetObjectives()

# Analyse order history
#for F in force:
#    print('Order history:')
#    for C in F.company:
#        print(C.order_history)
#        for P in C.platoon:
##            print(P.order_history)
#            for S in P.section:
##                print(S.order_history)
#                pass