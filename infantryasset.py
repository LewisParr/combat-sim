# -*- coding: utf-8 -*-
# infantryasset.py

import numpy as np

class InfantryAsset(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """        
    def setLocation(self, location):
        self.location = location
    
    def detect(self, env, enemy_force):
        # Find visibility cell
        cell_x = int(np.floor(self.location[0] / env.visibility_cell_width))
        cell_y = int(np.floor(self.location[1] / env.visibility_cell_width))
        # Fetch the visibility map
        v_map = np.asarray(env.visibility_cell[cell_x][cell_y].v_map)
        # Find enemy assets' location and check for detection
        detected_location = []
        for C in enemy_force.company:
            for P in C.platoon:
                for S in P.section:
                    for M in S.unit.member:
                        cell_x = int(np.floor(M.location[0] / env.visibility_cell_width))
                        cell_y = int(np.floor(M.location[1] / env.visibility_cell_width))
                        raw_detection_prob = v_map[cell_x][cell_y]
                        # Random sample test for detection
                        random_sample = np.random.uniform()
                        if random_sample < raw_detection_prob:
                            # Asset is detected, create detection event
                            # ADD UNCERTAINTY HERE?
                            detected_location.append([M.location[0], M.location[1]])
        return detected_location
    
    def moveTo(self, target):
        x_dist = target[0] - self.location[0]
        y_dist = target[1] - self.location[1]
        dist = np.sqrt(x_dist**2 + y_dist**2)
        x_change = (x_dist / dist) * self.max_speed
        y_change = (y_dist / dist) * self.max_speed
        return [self.manID, [x_change, y_change]]
    
    def applyEvents(self):
        for E in self.event:
            E.apply()

class Rifleman(InfantryAsset):
    """
    Rifleman represents an infantryman equipped primarily with small arms
    rifle variants.
    """
    def __init__(self, riflemanID):
        self.manID = riflemanID
        self.max_speed = 5

class AutomaticRifleman(InfantryAsset):
    """
    AutomaticRifleman represents an infantryman equipped primarily with small
    arms light machine gun or light support weapon variants.
    """
    def __init__(self, autoriflemanID):
        self.manID = autoriflemanID
        self.max_speed = 5
        
class Marksman(InfantryAsset):
    """
    Marksman represents an infantryman equipped primarily with small arms
    marksman rifle variants.
    """
    def __init__(self, marksmanID):
        self.manID = marksmanID
        self.max_speed = 5