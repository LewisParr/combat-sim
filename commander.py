# -*- coding: utf-8 -*-
# commander.py

import infantryasset

import numpy as np

class Commander(object):
    """
    Commander is base class providing an interface for all subsequent
    (inherited) commander roles that will handle primary decision making 
    at each tier of the command structure.
    """
    pass

class TopLevelCommander(Commander):
    """
    TopLevelCommander provides an interface for the commanders most senior in
    the friendly and enemy forces.
    """
    def __init__(self):
        pass
    
    def assignObjective(self, objective):
        self.objective = objective
        
    def assignAssets(self, assets):
        nCompany = len(assets)
        self.company = []
        for C in np.arange(0, nCompany):
            self.company.append(CompanyCommander(assets[C]))
    
    def assignAssetLocations(self, locations):
        for C in np.arange(0, len(self.company)):
            for P in np.arange(0, len(self.company[C].platoon)):
                for S in np.arange(0, len(self.company[C].platoon[P].section)):
                    self.company[C].platoon[P].section[S].setLocation(locations[C][P][S])
            
class FriendlyCommander(TopLevelCommander):
    """
    FriendlyCommander acts as the top level decision maker for the friendly 
    forces.
    """
    pass

class EnemyCommander(TopLevelCommander):
    """
    EnemyCommander acts as the top level decision maker for the enemy forces.
    """
    pass

class SectionCommander(Commander):
    """
    SectionCommander handles the receiving of information from members of the
    section and communicates information to and from a superior commander.
    """
    def __init__(self, nRifleman=2, nAutomaticRifleman=1, nMarksman=1):
        self.rifleman = []
        for R in np.arange(0, nRifleman):
            self.rifleman.append(infantryasset.Rifleman())
        self.autorifleman = []
        for A in np.arange(0, nAutomaticRifleman):
            self.autorifleman.append(infantryasset.AutomaticRifleman())
        self.marksman = []
        for M in np.arange(0, nMarksman):
            self.marksman.append(infantryasset.Marksman())
    
    def setLocation(self, location):
        """
        location = [x, y] coordinates of section.
        """
        self.location = location

class PlatoonCommander(Commander):
    """
    PlatoonCommander handles the receiving of information from members of the
    platoon and communicates information to and from superior and inferior
    commanders.
    """
    def __init__(self, assets):
        nSection = assets
        self.section = []
        for S in np.arange(0, nSection):
            self.section.append(SectionCommander())
    pass

class CompanyCommander(Commander):
    """
    CompanyCommander handles the receiving of information from members of the 
    company and communicates information to and from superior and inferior 
    commanders.
    """
    def __init__(self, assets):
        nPlatoon = len(assets)
        self.platoon = []
        for P in np.arange(0, nPlatoon):
            self.platoon.append(PlatoonCommander(assets[P]))
        
    pass