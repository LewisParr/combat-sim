# -*- coding: utf-8 -*-
# simulation.py

import scenario
import environment
import commander
import event

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def timestep():
    # Detection
    for F in force:
        F.detect(env, force[F.enemy_forceID])
    # Assess objective states
    for F in force:
        F.updateObjectiveStatus(env, force[F.enemy_forceID].hq.member.location)
    # Give orders
    for F in force:
        F.giveOrders(env)
    # Event creation
    event_queue = []
    for F in force:
        [forceID, companyID, platoonID, sectionID, manID, eventType, eventData] = F.createEvents(env, force[F.enemy_forceID])
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
                            event_queue.append(event.FireEvent(source, target, eventData[a][b][c][d][1]))
    # Event effect calculation
    for E in event_queue:
        if E.type == 'MOVE':
            pass
        elif E.type == 'FIRE':
            E.calculate()
    # Event result application
    for E in event_queue:
        if E.type == 'MOVE':
            E.apply(force)
        elif E.type == 'FIRE':
            E.apply(force)
    # Find number of surviving assets
    count = []
    for F in force:
        count.append(F.countActive())
    print('Surviving Assets: %s' % count)
    # Record the state of each force
    for F in force:
        F.record(env)

def end_simulation():
    for F in force:
        F.end_simulation()

# Initialise environment
print('Initialising environment...')
#env = environment.Environment(260, 260)
print('Generating terrain...')
#env.genTerrain(1)
#env.saveElevationData()
#env.loadElevationData()

# Plot terrain
print('Plotting terrain...')
env.plotElevation()

# Build visibility maps
print('Building visibility maps...')
#env.buildVisibilityMaps()
#env.saveVisibilityMaps()
#env.loadVisibilityMaps()

# Initialise scenario
print('Initialising scenario...')
scene = scenario.TestScenario()

# Initialise commanders
print('Initialising commanders...')
force = []
force.append(commander.EnemyCommander(0))
force.append(commander.FriendlyCommander(1))
force[0].assignObjective(scene.adversary_objective)
force[0].assignAssets(scene.adversary_assets)
force[0].assignAssetLocations(scene.adversary_asset_locations, scene.adversary_fob_location)
force[1].assignObjective(scene.friendly_objective)
force[1].assignAssets(scene.friendly_assets)
force[1].assignAssetLocations(scene.friendly_asset_locations, scene.friendly_fob_location)

# Create graph of enemy assets
E = nx.DiGraph()
color_map = []
E.add_node(force[0])
color_map.append('red')
for C in force[0].company:
    E.add_node(C)
    color_map.append('orange')
    E.add_edge(force[0],C)
    for P in C.platoon:
        E.add_node(P)
        color_map.append('yellow')
        E.add_edge(C,P)
        for S in P.section:
            E.add_node(S)
            color_map.append('green')
            E.add_edge(P,S)

# Draw graph of enemy assets
#plt.figure()
#plt.title('Enemy Assets')
#nx.draw(E, node_color=color_map)
#plt.show()

# Create graph of friendly assets
F = nx.DiGraph()
color_map = []
F.add_node(force[1])
color_map.append('red')
for C in force[1].company:
    F.add_node(C)
    color_map.append('orange')
    F.add_edge(force[1],C)
    for P in C.platoon:
        F.add_node(P)
        color_map.append('yellow')
        F.add_edge(C,P)
        for S in P.section:
            F.add_node(S)
            color_map.append('green')
            F.add_edge(P,S)

# Draw graph of friendly assets
#plt.figure()
#plt.title('Friendly Assets')
#nx.draw(F, node_color=color_map)
#plt.show()

# Plot asset locations
print('Plotting asset locations...')
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

# Develop general course of action
for F in force:
    F.decomposeObjective(F.objective, env)
    print('Number of objectives: %s' % nx.number_of_nodes(F.obj_graph))
    print('Number of dependecies: %s' % nx.number_of_edges(F.obj_graph))

# Assign assets to objectives
#for F in force:
#    F.assignAssetObjectives()

# Step through time
for t in np.arange(1, 51):
    print('Timestep: %s' % t)
    # Perform timestep operations
    timestep()
#    if np.mod(t, 1) == 0:
        # Plot asset locations
#        print('Plotting asset locations...')
#        X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
#        Z = env.getTerrainCellElevations()
#        plt.figure()
#        plt.contourf(X, Y, Z)
#        c = ['r', 'b']
#        a = 0
#        for F in force:
#            x = []
#            y = []
#            for C in np.arange(0, len(F.company)):
#                for P in np.arange(0, len(F.company[C].platoon)):
#                    for S in np.arange(0, len(F.company[C].platoon[P].section)):
#                        for M in np.arange(0, len(F.company[C].platoon[P].section[S].unit.member)):
#                            if F.company[C].platoon[P].section[S].unit.member[M].status != 2:
#                                x.append(F.company[C].platoon[P].section[S].unit.member[M].location[0])
#                                y.append(F.company[C].platoon[P].section[S].unit.member[M].location[1])
#            plt.scatter(x, y, c=c[a], marker='.')
#            plt.scatter(F.hq.member.location[0], F.hq.member.location[1], c=c[a], marker='x')
#            a += 1
#        plt.xlabel('X')
#        plt.ylabel('Y')
#        plt.title('Asset Location')
#        plt.show()
        # Plot detected enemy locations
#        print('Plotting detected enemy locations...')
#        X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
#        Z = env.getTerrainCellElevations()
#        plt.figure()
#        plt.contourf(X, Y, Z)
#        c = ['b', 'r'] # Colours are reversed (locations represent adversary)
#        a = 0
#        for F in force:
#            x = []
#            y = []
#            for l in F.detected_location:
#                x.append(l[0])
#                y.append(l[1])
#            plt.scatter(x, y, c=c[a], marker='.')
#            a += 1
#        plt.xlabel('X')
#        plt.ylabel('Y')
#        plt.title('Detected Enemy Asset Location')
#        plt.show()
end_simulation()

# Analyse order history
for F in force:
    print('Order history:')
    for C in F.company:
        print(C.order_history)
        for P in C.platoon:
            print(P.order_history)
            for S in P.section:
                print(S.order_history)
    
# Output results
# Number of active assets
plt.figure()
c = ['r', 'b']
a = 0
for F in force:
    plt.plot(F.active_assets, c=c[a])
    a += 1
plt.xlabel('Timestep')
plt.ylabel('Active Assets')
plt.title('Number of Active Assets')
# Visible area
plt.figure()
c = ['r', 'b']
a = 0
for F in force:
    plt.plot(F.visible_area, c=c[a])
    a += 1
plt.xlabel('Timestep')
plt.ylabel('Visible Area')
plt.title('Fraction of Environment Visible')
# Number of detected enemy assets
plt.figure()
c = ['r', 'b']
a = 0
for F in force:
    plt.plot(F.detected_enemy_assets, c=c[a])
    a += 1
plt.xlabel('Timestep')
plt.ylabel('Enemy Assets')
plt.title('Number of Detected Enemy Assets')