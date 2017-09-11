# -*- coding: utf-8 -*-
# scenerio.py

import objective

import numpy as np

class Scenario(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """
    pass

class TestScenario(Scenario):
    def __init__(self, speed):
        self.adversary_objective = objective.HoldArea([150, 200], [200, 150])
        self.friendly_objective = objective.TakeArea([150, 200], [200, 150])
        self.adversary_fob_location = [225, 225]
        self.friendly_fob_location = [25, 25]
        self.adversary_assets = [[2, 2, 2], [2, 2, 2]]
        self.friendly_assets = [[2, 2, 2], [2, 2, 2]]
        self.adversary_asset_locations = [[[[125, 210], [130, 230]], [[130, 200], [125, 205]], [[130, 200], [140, 200]]], [[[150, 190], [155, 175]], [[150, 175], [160, 200]], [[170, 180], [180, 180]]]]
        self.friendly_asset_locations = [[[[25, 25], [30, 25]], [[35, 25], [40, 25]], [[45, 25], [50, 25]]], [[[55, 25], [60, 25]], [[65, 25], [70, 25]], [[75, 25], [80, 25]]]]
        self.adversary_speed = speed[0]
        self.friendly_speed = speed[1]

class RandomScenario(Scenario):
    def __init__(self, size, speed):
        objective_ctr = [np.random.uniform(size[0] / 3, size[0] * 2 / 3), np.random.uniform(size[1] / 3, size[1] * 2 / 3)]
        random_sample = np.random.uniform(0.0, 1.0)
        if random_sample < 0.5:
            self.adversary_objective = objective.HoldArea([objective_ctr[0] - 25, objective_ctr[1] + 25], [objective_ctr[0] + 25, objective_ctr[1] - 25])
            self.friendly_objective = objective.TakeArea([objective_ctr[0] - 25, objective_ctr[1] + 25], [objective_ctr[0] + 25, objective_ctr[1] - 25])
        else:
            self.adversary_objective = objective.TakeArea([objective_ctr[0] - 25, objective_ctr[1] + 25], [objective_ctr[0] + 25, objective_ctr[1] - 25])
            self.friendly_objective = objective.HoldArea([objective_ctr[0] - 25, objective_ctr[1] + 25], [objective_ctr[0] + 25, objective_ctr[1] - 25])
        self.objective_ctr = objective_ctr
        self.adversary_fob_location = [None, None]
        for i in np.arange(0, 2):
            coord = np.random.uniform(0, size[i])
            valid = self.checkCoord(coord, i, size, False)
            while valid == False:
                coord = np.random.uniform(0, size[i])
                valid = self.checkCoord(coord, i, size, False)
            self.adversary_fob_location[i] = coord
        x_ctr = size[0] / 2
        y_ctr = size[1] / 2
        x_dist = x_ctr - self.adversary_fob_location[0]
        y_dist = y_ctr - self.adversary_fob_location[1]
        self.friendly_fob_location = [self.adversary_fob_location[0] + (2 * x_dist), self.adversary_fob_location[1] + (2 * y_dist)]
        self.adversary_assets = [[2, 2, 2], [2, 2, 2]]
        self.friendly_assets = [[2, 2, 2], [2, 2, 2]]
        self.adversary_asset_locations = [[[None, None], [None, None], [None, None]], [[None, None], [None, None], [None, None]]]
        for a in np.arange(0, len(self.adversary_assets)):
            company_ctr = [np.random.normal(loc=self.adversary_fob_location[0], scale=20), np.random.normal(loc=self.adversary_fob_location[1], scale=20)]
            valid = self.checkWithinEnvironment(company_ctr, size)
            while valid == False:
                company_ctr = [np.random.normal(loc=self.adversary_fob_location[0], scale=20), np.random.normal(loc=self.adversary_fob_location[1], scale=20)]
                valid = self.checkWithinEnvironment(company_ctr, size)
            for b in np.arange(0, len(self.adversary_assets[a])):
                platoon_ctr = [np.random.normal(loc=company_ctr[0], scale=10), np.random.normal(loc=company_ctr[1], scale=10)]
                valid = self.checkWithinEnvironment(platoon_ctr, size)
                while valid == False:
                    platoon_ctr = [np.random.normal(loc=company_ctr[0], scale=10), np.random.normal(loc=company_ctr[1], scale=10)]
                    valid = self.checkWithinEnvironment(platoon_ctr, size)
                for c in np.arange(0, self.adversary_assets[a][b]):
                    section_loc = [np.random.normal(loc=platoon_ctr[0], scale=5), np.random.normal(loc=platoon_ctr[1], scale=5)]
                    valid = self.checkWithinEnvironment(section_loc, size)
                    while valid == False:
                        section_loc = [np.random.normal(loc=platoon_ctr[0], scale=5), np.random.normal(loc=platoon_ctr[1], scale=5)]
                        valid = self.checkWithinEnvironment(section_loc, size)
                    self.adversary_asset_locations[a][b][c] = section_loc
        self.friendly_asset_locations = [[[None, None], [None, None], [None, None]], [[None, None], [None, None], [None, None]]]
        for a in np.arange(0, len(self.friendly_assets)):
            company_ctr = [np.random.normal(loc=self.friendly_fob_location[0], scale=20), np.random.normal(loc=self.friendly_fob_location[1], scale=20)]
            valid = self.checkWithinEnvironment(company_ctr, size)
            while valid == False:
                company_ctr = [np.random.normal(loc=self.friendly_fob_location[0], scale=20), np.random.normal(loc=self.friendly_fob_location[1], scale=20)]
                valid = self.checkWithinEnvironment(company_ctr, size)
            for b in np.arange(0, len(self.friendly_assets[a])):
                platoon_ctr = [np.random.normal(loc=company_ctr[0], scale=10), np.random.normal(loc=company_ctr[1], scale=10)]
                valid = self.checkWithinEnvironment(platoon_ctr, size)
                while valid == False:
                    platoon_ctr = [np.random.normal(loc=company_ctr[0], scale=10), np.random.normal(loc=company_ctr[1], scale=10)]
                    valid = self.checkWithinEnvironment(platoon_ctr, size)
                for c in np.arange(0, self.friendly_assets[a][b]):
                    section_loc = [np.random.normal(loc=platoon_ctr[0], scale=5), np.random.normal(loc=platoon_ctr[1], scale=5)]
                    valid = self.checkWithinEnvironment(section_loc, size)
                    while valid == False:
                        section_loc = [np.random.normal(loc=platoon_ctr[0], scale=5), np.random.normal(loc=platoon_ctr[1], scale=5)]
                        valid = self.checkWithinEnvironment(section_loc, size)
                    self.friendly_asset_locations[a][b][c] = section_loc
        self.adversary_speed = speed[0]
        self.friendly_speed = speed[1]
    
    def checkCoord(self, coord, dim, size, inside):
        if inside == False:
            valid = True
            if coord > size[dim] / 4:
                if coord < size[dim] * 3 / 4:
                    valid = False
            return valid
        else:
            valid = True
            if coord < size[dim] / 4:
                if coord > size[dim] * 3 / 4:
                    valid = False
            return valid
    
    def checkWithinEnvironment(self, coord, size):
        valid = True
        if coord[0] <= 0 + 20:
            valid = False
        elif coord[0] >= size[0] - 20:
            valid = False
        if coord[1] <= 0 + 20:
            valid = False
        elif coord[1] >= size[1] - 20:
            valid = False
        return valid