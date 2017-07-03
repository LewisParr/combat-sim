# -*- coding: utf-8 -*-
# objective.py

class Objective(object):
    """
    Objective is base class providing an interface for all subsequent 
    (inherited) objectives.
    """
    pass

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
        self.NW = NW
        self.SE = SE