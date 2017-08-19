# -*- coding: utf-8 -*-
# genetic.py

import fuzzy

import csv
import numpy as np

class Solution(object):
    def __init__(self):
        self.fitness = None
    
    def random(self):
        mission_obj_weight = np.random.uniform(low=0.0, high=5.0)
        priority_decay = np.random.uniform(low=0.1, high=0.9)
        friendly_fob_weight = np.random.uniform(low=0.0, high=5.0)
        spatial_influence_weight = np.random.uniform(low=0.0, high=5.0)
        visibility_influence_weight = np.random.uniform(low=0.0, high=5.0)
        enemy_fob_weight = np.random.uniform(low=0.0, high=5.0)
        enemy_threat_weight = np.random.uniform(low=0.0, high=5.0)
        control_threshold = np.random.uniform(low=0.0, high=5.0)
        priority_cutoff = np.random.uniform(low=0.1, high=0.9)
        self.parameters = [mission_obj_weight, priority_decay, friendly_fob_weight, spatial_influence_weight, visibility_influence_weight, enemy_fob_weight, enemy_threat_weight, control_threshold, priority_cutoff]
    
    def set_Parameters(self, parameters):
        self.parameters = parameters
    
    def mutate(self):
        mutation_scale = 0.5
        new_parameters = []
        for p in self.parameters:
            new_parameters.append(p + np.random.normal(loc=0.0, scale=mutation_scale))
        self.set_Parameters(new_parameters)

class Population(object):
    def __init__(self, size):
        self.solution = []
        for n in np.arange(0, size):
            self.solution.append(self.randomSolution())
        self.mean_fitness = []
        # Set the fuzzy logic rules for evaluation
        self.rule = []
        self.rule.append(fuzzy.AssetsKilled([[0.3, 0.7], [0.3, 0.7]], 3.0))
        self.rule.append(fuzzy.BattlespaceInformation([0.15, 0.25], 1.0))
    
    def randomSolution(self):
        new_solution = Solution()
        new_solution.random()
        return new_solution
    
    def chooseSolutions(self):
        # Select random solutions for evaluation (must be fewer than size of 
        # population)
        nSolutions = 3
        size = len(self.solution)
        candidates = list(map(int, np.linspace(0, size-1, num=size)))
        selected = []
        iselected = []
        for a in np.arange(0, nSolutions):
            i = np.random.randint(0, len(candidates))
            selection = candidates[i]
            selected.append(self.solution[selection])
            iselected.append(selection)
            candidates.pop(i)
        # Store selected solutions for later breeding, etc.
        self.selected = iselected
        # Output the selected solutions to be paired with adversary solutions
        # in simulation
        return selected
    
    def receive_Simulation_Result(self, i, assets_killed, battlespace_visibility):
        isolution = self.selected[i]
        values = [assets_killed, battlespace_visibility]
        i = 0
        strength = []
        for r in self.rule:
            strength.append(r.fireStrength(values[i]))
            i += 1
        fitness = 0
        for i in np.arange(0, len(self.rule)):
            fitness += strength[i] * self.rule[i].weight
        self.solution[isolution].fitness = fitness
        # Record details for analysis (not part of simulation/algorithm)
        parameters = self.solution[isolution].parameters
        output = parameters + assets_killed + battlespace_visibility + fitness
        with open('fitness.txt', 'w') as output_file:
            wr = csv.writer(output_file)
            wr.writerow(output)
    
    def breed(self):
        # Select the number of children to breed (must use fewer parents than 
        # tested to improve average population fitness)
        nChildren = 1
        # Calculate the fitness-based weights for breeding selection
        fitness = []
        for a in self.selected:
            fitness.append(self.solution[a].fitness)
        # Save the mean fitness of the tested solutions
        self.mean_fitness.append(np.mean(fitness))
        # Adjust for selection
        cum_fitness = [fitness[0]]
        for i in np.arange(1, len(fitness)):
            cum_fitness.append(cum_fitness[-1] + fitness[i])
        selection_weight = np.asarray(cum_fitness) / cum_fitness[-1]
        for c in np.arange(0, nChildren):
            # Select parents
            # For now, allow the same parent to be selected twice
            parent = []
            for p in np.arange(0, 2):
                random_sample = np.random.uniform(low=0.0, high=1.0)
                found = False
                i = 0
                if random_sample < selection_weight[0]:
                    found = True
                else:
                    while found == False:
                        i += 1
                        if random_sample > selection_weight[i-1]:
                            if random_sample < selection_weight[i]:
                                found = True
                iselected = self.selected[i]
                parent.append(self.solution[iselected])
            # Perform crossover
            parameters = self.crossover(parent)
            # Create child
            child = Solution()
            child.set_Parameters(parameters)
            child.mutate()
            # Add child to population
            self.solution.append(child)
            # Kill underperforming solutions
            self.purge()
            
    def crossover(self, parent):
        # Get the parents' parameters
        parameters = []
        for p in parent:
            parameters.append(p.parameters)
        # Randomly select crossover point
        i = np.random.randint(low=1, high=len(parameters[0]))
        # Build new parameters
        new_parameters = []
        for a in np.arange(0, len(parameters[0])):
            if a <= i:
                new_parameters.append(parameters[0][a])
            else:
                new_parameters.append(parameters[1][a])
        return new_parameters
    
    def purge(self):
        pass