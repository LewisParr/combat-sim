# -*- coding: utf-8 -*-
# scenerio.py

import objective

class Scenario(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """
    pass

class TestScenario(Scenario):
    """
    ...
    """
    def __init__(self):
        self.adversary_objective = objective.HoldArea([150, 200], [200, 150])
        self.friendly_objective = objective.TakeArea([150, 200], [200, 150])
        self.adversary_assets = [[2, 2, 2], [2, 2, 2]]
        self.friendly_assets = [[2, 2, 2], [2, 2, 2]]
        self.adversary_asset_locations = [[[[125, 210], [130, 230]], [[130, 200], [125, 205]], [[130, 200], [140, 200]]], [[[150, 190], [155, 175]], [[150, 175], [160, 200]], [[170, 180], [180, 180]]]]
        self.friendly_asset_locations = [[[[25, 25], [30, 25]], [[35, 25], [40, 25]], [[45, 25], [50, 25]]], [[[55, 25], [60, 25]], [[65, 25], [70, 25]], [[75, 25], [80, 25]]]]
        