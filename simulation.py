# -*- coding: utf-8 -*-
# simulation.py

import genetic
import scenario
import environment
import commander
import event

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

np.random.seed(111)

class Simulation_Result(object):                                                # Results for single force in single simulation
    def __init__(self, forceID, moType, parameters, fitness, active_assets, detected_enemy_assets, visible_area, mo_score):
        self.forceID = forceID
        self.moType = moType
        self.parameters = parameters
        self.fitness = fitness
        self.active_assets = active_assets
        self.detected_enemy_assets = detected_enemy_assets
        self.visible_area = visible_area
        self.mo_score = mo_score
        self.mo_result = None
    
    def get_force_size(self):
        self.force_size = self.active_assets[0]
    
    def get_mo_success(self, score):
        if self.forceID == 0:
            self.mo_result = -score
        else:
            self.mo_result = score

class Optimisation_Result(object):
    def __init__(self, nGenerations, nInitialSize, nChildren, nPurge):
        self.simulation_result = [[], []]
        self.event_data = []
        self.scenario_data = []
        self.nGeneration = nGenerations
        self.nInitialSize = nInitialSize
        self.nChildren = nChildren
        self.nPurge = nPurge
    
    def add_simulation_result(self, forceID, sr):
        self.simulation_result[forceID].append(sr)
    
    def add_scenario_data(self, fob_loc, mo_loc):
        self.scenario_data.append([fob_loc, mo_loc])
    
    def add_event_data(self, event_data):
        self.event_data.append(event_data)
        
    def analyse(self):
        # Save the initial force sizes
        for fsr in self.simulation_result:
            for sr in fsr:
                sr.get_force_size()
        # Save the relative MO scores for each simulation
        self.relative_mo_score = []                                             # Positive if blue relatively higher
        for i in np.arange(0, len(self.simulation_result[0])):
            mo_score = []
            for j in np.arange(0, 2):
                mo_score.append(self.simulation_result[j][i].mo_score)
            s_relative_mo_score = []
            for t in np.arange(0, len(mo_score[0])):
                print(mo_score[1][t])
                print(mo_score[0][t])
                print(mo_score[1][t] - mo_score[0][t])
                s_relative_mo_score.append(mo_score[1][t] - mo_score[0][t])
            self.relative_mo_score.append(s_relative_mo_score)
        # Plot relative MO scores
        plt.figure()
        for sr_rel_mo_score in self.relative_mo_score:
            plt.plot(sr_rel_mo_score)
        plt.show()
        # Save the mission objective success
        for fsr in self.simulation_result:
            i = 0
            for sr in fsr:
                print(self.relative_mo_score[i][-1])
                sr.get_mo_success(self.relative_mo_score[i][-1])
                i += 1
        # ---***--- LOCAL OPTIMISATION ---***---
        # HOW DOES EACH PARAMETER AFFECT THE SOLUTION FITNESS?
        # Multiple regression
        # ...
        # Linear regression
        for p in np.arange(0, len(self.simulation_result[0][0].parameters)):
            p_value = []
            f_value = []
            moType = []
            for fsr in self.simulation_result:
                for sr in fsr:
                    p_value.append(sr.parameters[p])
                    f_value.append(sr.fitness)
                    if sr.moType == 'HOLD AREA':
                        moType.append(0)
                    elif sr.moType == 'TAKE AREA':
                        moType.append(1)
            # Plot relationship (scatter)
            plt.figure()
            plt.scatter(p_value, f_value, c=moType, marker='x')
            plt.xlabel('Parameter Value')
            plt.ylabel('Fitness Value')
            plt.title('Parameter %s - Fitness Relationship' % p)
            plt.show()
            slope, intercept, r_value, p_value, std_err = stats.linregress(p_value,f_value)
            print('Slope: %s' % slope)
            print('Intercept: %s' % intercept)
            print('R: %s' % r_value)
            print('p: %s' % p_value)
            print('Standard Error: %s' % std_err)
        # Analysis of variance
        # ...
        # ANALYSE FIRE EVENT LOCATIONS
        source_loc = [[], []]
        target_loc = [[], []]
        hit_result = []
        for sr in self.event_data:
            for t in sr:
                for e in t:
                    if e.type == 'FIRE':
                        for i in np.arange(0, 2):
                            source_loc[i].append(e.source_loc[i])
                            target_loc[i].append(e.target_loc[i])
                        hit_result.append(e.hit_result)
        # Plot source locations
        plt.figure()
        plt.scatter(source_loc[0], source_loc[1], c=hit_result, marker='x')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Fire Event Source Locations')
        plt.show()
        # X Distribution (source)
        plt.figure()
        plt.hist(source_loc[0])
        plt.xlabel('X')
        plt.ylabel('Frequency')
        plt.title('Fire Event Source X Distribution')
        plt.show()
        # Y Distribution (source)
        plt.figure()
        plt.hist(source_loc[1])
        plt.xlabel('Y')
        plt.ylabel('Frequency')
        plt.title('Fire Event Source Y Distribution')
        plt.show()
        # Plot target locations
        plt.figure()
        plt.scatter(target_loc[0], target_loc[1], c=hit_result, marker='x')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Fire Event Target Locations')
        plt.show()
        # X Distribution (target)
        plt.figure()
        plt.hist(target_loc[0])
        plt.xlabel('X')
        plt.ylabel('Frequency')
        plt.title('Fire Event Source X Distribution')
        plt.show()
        # Y Distribution (target)
        plt.figure()
        plt.hist(target_loc[1])
        plt.xlabel('Y')
        plt.ylabel('Frequency')
        plt.title('Fire Event Source Y Distribution')
        plt.show()

class Optimise(object):
    def __init__(self, goal, nInitialSolutions, nGenerations, nChoose, nChildren, nPurge):
        print('Running optimisation for %s generations...' % nGenerations)
        self.goal = goal
        self.nInitialSolutions = nInitialSolutions
        self.nGenerations = nGenerations
        self.nChoose = nChoose
        self.nChildren = nChildren
        self.nPurge = nPurge
        self.detected_enemy_assets = [[], []]
        self.result = Optimisation_Result(nGenerations, nInitialSolutions, nChildren, nPurge)
        self.create_Populations()
        self.solve()
        
    def create_Populations(self):
        self.pop = []
        for i in np.arange(0, 2):
            self.pop.append(genetic.Population(self.nInitialSolutions))
    
    def solve(self):
        for g in np.arange(0, self.nGenerations):                               # Repeat process for given number of generations
            print('Generation %s of %s...' % (g+1, self.nGenerations))
            if g != 0:                                                          # Generate a new environment and scenario if optimising globally and this is not the first generation
                if self.goal == 'GLOBAL':
                    self.env = generate_Environment()
                    scene = scenario.RandomScenario([self.env.nX, self.env.nY], [[0.40, 0.05], [0.40, 0.05]])
            else:
                self.env = generate_Environment()
                scene = scenario.RandomScenario([self.env.nX, self.env.nY], [[0.40, 0.05], [0.40, 0.05]])
            selected = []                                                       # Select solutions for simulation in this generation
            for i in np.arange(0, 2):
                selected.append(self.pop[i].chooseSolutions(self.nChoose))
            for a in np.arange(0, len(selected[0])):                            # Simulate each solution pair
                print('Running simulation %s of %s in generation %s...' % (a+1, len(selected[0]), g+1))
                self.event_history = []
                self.initialise_forces(selected, a, scene)                      # Initialise the forces
                plot_Locations(self.env, self.force)                            # Plot asset locations
                self.forces_planning()                                          # Perform COA planning
                for t in np.arange(1, 201):                                     # Step through time
                    print('Timestep %s of %s...' % (t, 200))
                    self.timestep()                                             # Perform timestep operations
                    if np.mod(t, 999) == 0:
                        plot_Locations(self.env, self.force)
                        plot_Detected(self.env, self.force)
                self.end_simulation()
                # Record
                self.record_positions()
                # Plot results
#                plot_Number_Active(self.force)
#                plot_Visible_Area(self.force)
#                plot_Number_Detected(self.force)
#                plot_Position_History(self.force)
                # Assess solution fitness
                print('Evaluating force performance...')
                adversary_assets_survived = self.force[0].active_assets[-1] / self.force[0].active_assets[0]
                friendly_assets_survived = self.force[1].active_assets[-1] / self.force[1].active_assets[0]
                adversary_assets_killed = 1 - friendly_assets_survived
                friendly_assets_killed = 1 - adversary_assets_survived
                adversary_battlespace_visibility = np.mean(self.force[0].visible_area)
                friendly_battlespace_visibility = np.mean(self.force[0].visible_area)
                fitness = [None, None]
                fitness[0] = self.pop[0].receive_Simulation_Result(a, [adversary_assets_killed, adversary_assets_survived], [adversary_battlespace_visibility])
                fitness[1] = self.pop[1].receive_Simulation_Result(a, [friendly_assets_killed, friendly_assets_survived], [friendly_battlespace_visibility])
                # Create simulation result objects
                print('Recording simulation results...')
                for i in np.arange(0, len(self.force)):
                    sr = Simulation_Result(self.force[i].forceID, self.force[i].objective.type, selected[i][a].parameters, fitness[i], self.force[i].active_assets, self.force[i].detected_enemy_assets, self.force[i].visible_area, self.force[i].mo_score)
                    self.result.add_simulation_result(i, sr)
                self.result.add_event_data(self.event_history)
                self.result.add_scenario_data([scene.adversary_fob_location, scene.friendly_fob_location], scene.objective_ctr)
            if g < self.nGenerations-1:
                for p in self.pop:                                              # Breed populations
                    p.breed(self.nChildren, self.nPurge)
            else:
                self.end_solve()
    
    def timestep(self):
        # Detection
        for F in self.force:
            F.detect(self.env, self.force[F.enemy_forceID])
        # Event creation
        event_queue = []
        for F in self.force:
            [forceID, companyID, platoonID, sectionID, manID, eventType, eventData] = F.createEvents(self.env, self.force[F.enemy_forceID])
            for a in np.arange(0, len(forceID)):
                for b in np.arange(0, len(companyID[a])):
                    for c in np.arange(0, len(platoonID[a][b])):
                        for d in np.arange(0, len(sectionID[a][b][c])):
                            if F.company[companyID[a][b]].platoon[platoonID[a][b][c]].section[sectionID[a][b][c][d]].unit.member[manID[a][b][c][d]].morale < 0.1:
                                source = [forceID[a], companyID[a][b], platoonID[a][b][c], sectionID[a][b][c][d], manID[a][b][c][d]]
                                speed = F.company[companyID[a][b]].platoon[platoonID[a][b][c]].section[sectionID[a][b][c][d]].unit.member[manID[a][b][c][d]].max_speed
                                event_queue.append(event.LowMoraleRetreat(source, speed))
                            else:
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
                E.apply(self.force, self.env.nX, self.env.nY)
            elif E.type == 'FIRE':
                E.apply(self.force)
            elif E.type == 'RETREAT':
                E.apply(self.force, self.env.nX, self.env.nY)
        # Store the events in history
        self.event_history.append(event_queue)
        # Find number of surviving assets
        count = []
        for F in self.force:
            count.append(F.countActive())
#        print('Surviving Assets: %s red; %s blue' % (count[0], count[1]))
        # Record the state of each force
        for F in self.force:
            F.record(self.env)
    
    def initialise_forces(self, selected, a, scene):
        self.force = []                                                         # Initialise commanders
        self.force.append(commander.TopLevelCommander(0, selected[0][a].parameters, scene.adversary_objective))
        self.force.append(commander.TopLevelCommander(1, selected[1][a].parameters, scene.friendly_objective))
        self.force[0].assignAssets(scene.adversary_assets, scene.adversary_speed)
        self.force[0].assignAssetLocations(scene.adversary_asset_locations, scene.adversary_fob_location)
        self.force[1].assignAssets(scene.friendly_assets, scene.friendly_speed)
        self.force[1].assignAssetLocations(scene.friendly_asset_locations, scene.friendly_fob_location)
    
    def forces_planning(self):
        for F in self.force:                                            # Battlegroup commander assign zones to companies
            F.assignZones(self.env, self.force[F.enemy_forceID].hq.member.location)
        plot_Zones(self.force, self.env)
        for F in self.force:                                            # Company commander assign COA to platoons
            for C in F.company:
                C.assignCOAPath(F.assignment, F.ctr, F.cost, F.priority, F.hq.member.location, F.objective.ctr, F.sector)
        plot_PlatoonCOA(self.force, self.env)
        for F in self.force:                                            # Platoon commander assign COA to sections
            for C in F.company:
                for P in C.platoon:
                    P.assignCOAPath(C.assignment, C.AO, C.sector_loc)
        plot_SectionCOA(self.force, self.env)
        for F in self.force:                                            # Section commander receives COA
            for C in F.company:
                for P in C.platoon:
                    for S in P.section:
                        S.assignPath(P.assignment, P.AO, P.sector_loc)

    def end_simulation(self):
        print('Terminating simulation...')
        for F in self.force:
            F.end_simulation()
    
    def end_solve(self):
        print('Ending optimisation...')
        print('Analysing results...')
        self.result.analyse()
        # Plot evolution of the mean fitness
        plt.figure()
        c = ['r', 'b']
        for i in np.arange(0, 2):
            plt.plot(self.pop[i].mean_fitness, c=c[i])
        plt.xlabel('Generation')
        plt.ylabel('Mean Fitness')
        plt.title('Mean Fitness of Tested Solutions')
        plt.show()
        # Plot evolution of the best fitness
        # ...
    
    def record_positions(self):
        pass

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
        plt.scatter(F.objective.ctr[0], F.objective.ctr[1], c=c[a])
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

def plot_Position_History(force):
    plt.figure()
    c = ['r', 'b']
    a = 0
    for F in force:
        for C in F.company:
            for P in C.platoon:
                for S in P.section:
                    for M in S.unit.member:
                        plt.plot(M.position_history, c=c[a])
        a += 1
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Position History')

def plot_Zones(force, env):
    for F in force:
        X, Y = np.meshgrid(np.arange(0, env.nX / 10), np.arange(0, env.nY / 10))
        Z = F.assignment
        plt.figure()
        plt.contourf(X, Y, Z)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Sector Assignment')
        plt.show()

def plot_PlatoonCOA(force, env):
    X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
    Z = env.getTerrainCellElevations()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.figure()
        plt.contourf(X, Y, Z)
        for C in F.company:
            for i in C.assignment:
                path = i[0]
                x_loc = []
                y_loc = []
                for s in path:
                    # Translate number to sector location
                    x_loc.append(C.sector_loc[s][0])
                    y_loc.append(C.sector_loc[s][1])
                plt.plot(x_loc, y_loc, c=c[a])
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Platoon COAs')
        plt.show()
        a += 1

def plot_SectionCOA(force, env):
    X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
    Z = env.getTerrainCellElevations()
    c = ['r', 'b']
    a = 0
    for F in force:
        plt.figure()
        plt.contourf(X, Y, Z)
        for C in F.company:
            for P in C.platoon:
                for i in P.assignment:
                    path = i[0]
                    x_loc = []
                    y_loc = []
                    for s in path:
                        x_loc.append(P.sector_loc[s][0])
                        y_loc.append(P.sector_loc[s][1])
                    plt.plot(x_loc, y_loc, c=c[a])
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Section COAs')
        plt.show()
        a += 1
        
nInitialSolutions = 3
nGenerations = 1
nChoose = 1
nChildren = 1
nPurge = 1
test = Optimise('LOCAL', nInitialSolutions, nGenerations, nChoose, nChildren, nPurge)