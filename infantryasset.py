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
        detected_location = []
        if self.status != 2:
            # Find visibility cell
            cell_x = int(np.floor(self.location[0] / env.visibility_cell_width))
            cell_y = int(np.floor(self.location[1] / env.visibility_cell_width))
            # Fetch the visibility map
            v_map = np.asarray(env.visibility_cell[cell_x][cell_y].v_map)
            # Find enemy assets' location and check for detection
            for C in enemy_force.company:
                for P in C.platoon:
                    for S in P.section:
                        for M in S.unit.member:
                            if M.status != 2:
                                cell_x = int(np.floor(M.location[0] / env.visibility_cell_width))
                                cell_y = int(np.floor(M.location[1] / env.visibility_cell_width))
                                raw_detection_prob = v_map[cell_x][cell_y]
                                # Get concealment value and use in detection chance
                                # Random sample test for detection
                                random_sample = np.random.uniform()
                                if random_sample < raw_detection_prob:
                                    cell_x = int(np.around(M.location[0]))
                                    cell_y = int(np.around(M.location[1]))
                                    concealment = env.terrain_cell[cell_x][cell_y].concealment
                                    random_sample = np.random.uniform()
                                    if random_sample < concealment:
                                        # Asset is detected, create detection event
                                        detected_location.append([M.location[0], M.location[1]])
        self.detected_location = detected_location
        return detected_location
    
    def moveTo(self, target):
        if self.status != 2:
            x_dist = target[0] - self.location[0]
            y_dist = target[1] - self.location[1]
            dist = np.sqrt(x_dist**2 + y_dist**2)
            x_change = (x_dist / dist) * self.max_speed
            y_change = (y_dist / dist) * self.max_speed
            return [self.manID, [x_change, y_change]]
        else:
            return [[], []]
    
    def fireRandomTarget(self, enemy_force, env):
        if self.status != 2:
            if len(self.detected_location) > 0:
                # Get subset of detected enemy assets that are within effective range
                valid_location = []
                for l in self.detected_location:
                    x_dist = l[0] - self.location[0]
                    y_dist = l[1] - self.location[1]
                    dist = np.sqrt(x_dist**2 + y_dist**2)
                    if dist <= self.effective_range:
                        valid_location.append(l)
                # Select a valid target
                if len(valid_location) > 0:
                    if len(valid_location) > 1:
                        target = np.random.randint(low=0, high=len(valid_location)-1)
                    else:
                        target = 0
                    target_x = valid_location[target][0]
                    target_y = valid_location[target][1]
                    for C in enemy_force.company:
                        for P in C.platoon:
                            for S in P.section:
                                for M in S.unit.member:
                                    x = M.location[0]
                                    y = M.location[1]
                                    if x == target_x:
                                        if y == target_y:
                                            target_manID = M.manID
                                            target_sectionID = S.sectionID
                                            target_platoonID = P.platoonID
                                            target_companyID = C.companyID
                                            target_forceID = enemy_force.forceID
                                            # Get cover value and send with event data
                                            cell_x = int(np.around(x))
                                            cell_y = int(np.around(y))
                                            cover = env.terrain_cell[cell_x][cell_y].cover
                    return [self.manID, [[target_forceID, target_companyID, target_platoonID, target_sectionID, target_manID], self.phit, cover]]
                else:
                    return [[], []]
            else:
                return [[], []]
        else:
            return [[], []]
    
    def fortify(self):
        if self.status != 2:
            self.fortification += self.fortification_rate
            if self.fortification >= 1.0:
                self.fortification = 1.0
    
    def applyEvents(self):
        for E in self.event:
            E.apply()
    
    def hit(self):
        self.status = 2 # Set status to killed
    
    def record_position(self):
        self.position_history.append(self.location)

class Rifleman(InfantryAsset):
    """
    Rifleman represents an infantryman equipped primarily with small arms
    rifle variants.
    """
    def __init__(self, riflemanID):
        self.manID = riflemanID
        self.max_speed = 5
        self.effective_range = 50
        self.phit = 0.5
        self.status = 0
        self.fortification = 0
        self.fortification_rate = 0.25
        self.morale = 1.0
        self.position_history = []

class AutomaticRifleman(InfantryAsset):
    """
    AutomaticRifleman represents an infantryman equipped primarily with small
    arms light machine gun or light support weapon variants.
    """
    def __init__(self, autoriflemanID):
        self.manID = autoriflemanID
        self.max_speed = 5
        self.effective_range = 50
        self.phit = 0.5
        self.status = 0
        self.fortification = 0
        self.fortification_rate = 0.25
        self.morale = 1.0
        self.position_history = []
        
class Marksman(InfantryAsset):
    """
    Marksman represents an infantryman equipped primarily with small arms
    marksman rifle variants.
    """
    def __init__(self, marksmanID):
        self.manID = marksmanID
        self.max_speed = 5
        self.effective_range = 75
        self.phit = 0.5
        self.status = 0
        self.fortification = 0
        self.fortification_rate = 0.20
        self.morale = 1.0
        self.position_history = []