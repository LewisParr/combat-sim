# -*- coding: utf-8 -*-
# simulation.py

import scenario
import environment
import commander

import matplotlib.pyplot as plt

# Initialise environment
print('Initialising environment...')
env = environment.Environment()
print('Generating terrain...')
env.genTerrain(250, 250, 2)

# Plot terrain
print('Plotting terrain...')
plt.figure()
plt.contourf(env.X, env.Y, env.Z)
plt.title('Elevation Contour Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Terrain Elevation')
plt.colorbar()
plt.show()

# Initialise scenario
print('Initialising scenario...')
scene = scenario.TestScenario()

# Initialise enemy commander
print('Initialising adversary forces...')
adversary = commander.EnemyCommander()
adversary.assignObjective(scene.adversary_objective)
adversary.assignAssets(scene.adversary_assets)
adversary.assignAssetLocations(scene.adversary_asset_locations)

# Initialise friendly commander
print('Initialising friendly forces...')
friendly = commander.FriendlyCommander()
friendly.assignObjective(scene.friendly_objective)
friendly.assignAssets(scene.friendly_assets)
friendly.assignAssetLocations(scene.friendly_asset_locations)

# Plot asset locations
print('Plotting asset locations...')
plt.figure()
plt.contourf(env.X, env.Y, env.Z)
x = []
y = []
for C in np.arange(0, len(adversary.company)):
    for P in np.arange(0, len(adversary.company[C].platoon)):
        for S in np.arange(0, len(adversary.company[C].platoon[P].section)):
            x.append(adversary.company[C].platoon[P].section[S].location[0])
            y.append(adversary.company[C].platoon[P].section[S].location[1])
plt.scatter(x, y, c='r', marker='.')
x = []
y = []
for C in np.arange(0, len(friendly.company)):
    for P in np.arange(0, len(friendly.company[C].platoon)):
        for S in np.arange(0, len(friendly.company[C].platoon[P].section)):
            x.append(friendly.company[C].platoon[P].section[S].location[0])
            y.append(friendly.company[C].platoon[P].section[S].location[1])
plt.scatter(x, y, c='b', marker='.')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Asset Location')
plt.show()