# -*- coding: utf-8 -*-
# objective.py

import numpy as np
import matplotlib.pyplot as plt

class Objective(object):
    """
    Objective is base class providing an interface for all subsequent 
    (inherited) objectives.
    """
    def identifyThreats(self, env):
        """
        identifyThreats will return regions of the environment from which the
        given region can receive fire and/or be detected.
        """
        x_ctr = (self.NW[0] + self.SE[0]) / 2
        y_ctr = (self.NW[1] + self.SE[1]) / 2
        # Find visibility cell
        cell_x = int(np.floor(x_ctr / env.visibility_cell_width))
        cell_y = int(np.floor(y_ctr / env.visibility_cell_width))
        # Fetch the visibility map
        v_map = np.asarray(env.visibility_cell[cell_x][cell_y].v_map)
        # Set the visibility probability cutoff
        cutoff = 0.44                                                           # NEED TO ADJUST THIS VALUE TO VISIBILITY MAPS, MAYBE BASED ON MEAN VISIBILITY?
        # Find locations with visibility probability above the cutoff           # ARE THERE ANY OTHER WAYS OF IDENTIFYING (DIFFERENT) OBJECTIVES?
        [x, y] = np.where(v_map > cutoff)
        # Plot these locations
#        plt.figure()
#        plt.scatter(x, y)
#        plt.title('Locations Exceeding Cutoff')
#        plt.show()
        # Return the visibility cell (x, y) values of threatening cells
        return [x, y]

class HoldArea(Objective):
    """
    HoldArea represents the mission objective of preventing a region of the 
    environment from falling into enemy control.
    """
    def __init__(self, NW, SE):
        """
        NW = [x, y] coordinates for the North-West corner of the region.
        SE = [x, y] coordinates for the South-East corner of the region.
        """
        self.type = "HOLD AREA"
        self.NW = NW
        self.SE = SE

class TakeArea(Objective):
    """
    TakeArea represent the mission objective of bringing a region of the 
    environment into friendly control.
    """
    def __init__(self, NW, SE):
        """
        NW = [x, y] coordinates for the North-West corner of the region.
        SE = [x, y] coordinates for teh South-East corner of the region.
        """
        self.type = "TAKE AREA"
        self.NW = NW
        self.SE = SE

class ThreatArea(Objective):
    """
    ...
    """
    def __init__(self, NW, SE):
        """
        ...
        """
        self.type = "THREAT AREA"
        self.NW = NW
        self.SE = SE