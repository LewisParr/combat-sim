# -*- coding: utf-8 -*-
# event.py

import numpy as np

class Event(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """
    pass

class MovementEvent(object):
    """
    ...
    """
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