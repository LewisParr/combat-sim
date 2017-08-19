# -*- coding: utf-8 -*-
# event.py

import numpy as np

class Event(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """
    pass

class MovementEvent(Event):
    def __init__(self, source, change):
        """
        change - [x, y] changes relative to current location
        """
        self.type = 'MOVE'
        self.source = source
        self.change = change
    
    def apply(self, force):
        for i in np.arange(0, len(force[self.source[0]].company[self.source[1]].platoon[self.source[2]].section[self.source[3]].unit.member[self.source[4]].location)):
            force[self.source[0]].company[self.source[1]].platoon[self.source[2]].section[self.source[3]].unit.member[self.source[4]].location[i] += self.change[i]

class FireEvent(Event):
    def __init__(self, source, target, phit, cover):
        self.type = 'FIRE'
        self.source = source
        self.target = target
        self.phit = phit
        self.cover = cover
    
    def calculate(self):
        random_sample = np.random.uniform(low=0.0, high=1.0)
        if random_sample < self.phit:
            random_sample = np.random.uniform(low=0.0, high=1.0)
            if random_sample < self.cover:
                self.hit_result = True
            else:
                self.hit_result = False
        else:
            self.hit_result = False
    
    def apply(self, force):
        if self.hit_result == True:
            force[self.target[0]].company[self.target[1]].platoon[self.target[2]].section[self.target[3]].unit.member[self.target[4]].hit()
            force[self.target[0]].company[self.target[1]].platoon[self.target[2]].section[self.target[3]].unit.hit()

class LowMoraleRetreat(Event):
    def __init__(self, source, speed):
        self.type = 'RETREAT'
        self.source = source
        x_change = np.random.uniform(0, speed)
        y_change = np.sqrt(speed**2 - x_change**2)
        self.change = [x_change, y_change]
    
    def apply(self, force):
        for i in np.arange(0, len(force[self.source[0]].company[self.source[1]].platoon[self.source[2]].section[self.source[3]].unit.member[self.source[4]].location)):
            force[self.source[0]].company[self.source[1]].platoon[self.source[2]].section[self.source[3]].unit.member[self.source[4]].location[i] += self.change[i]