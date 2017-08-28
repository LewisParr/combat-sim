# -*- coding: utf-8 -*-
# section.py

import unit

unitIDs = {2 : unit.Infantry,
           7 : unit.Sniper}

class SectionCommander(object):
    """
    SectionCommander handles the receiving of information from members of the
    section and communicates information to and from a superior commander.
    """
    def __init__(self, sectionID, unitID=2):
        self.sectionID = sectionID
        self.unit = unitIDs[unitID]()
        self.detected_location = []
        self.order = None
        self.order_history = []
        self.order_duration = 0
    
    def setLocation(self, location):
        self.location = location
        self.unit.setLocation(location)
    
    def assignPath(self, assignment, graph, sector_loc):
        # First location of assignment is friendly FOB and assumed to be already
        # achieved.
        assigned = assignment[self.sectionID][0]
        self.achieved = [False] * len(assigned)
        self.achieved[0] = True
    
    def detect(self, env, enemy_force):
        detected_location = self.unit.detect(env, enemy_force)
        self.detected_location = detected_location
        return detected_location
    
    def createEvents(self, env, enemy_force):
        [manID, eventType, eventData] = self.unit.createEvents(env, enemy_force)
        sectionID = [self.sectionID] * len(manID)
        return [sectionID, manID, eventType, eventData]