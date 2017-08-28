# -*- coding: utf-8 -*-
# section.py

import unit
import order

import numpy as np

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
        self.assigned = assignment[self.sectionID][0]
        self.sector_loc = sector_loc
        self.achieved = [False] * len(self.assigned)
        self.achieved[0] = True
    
    def detect(self, env, enemy_force):
        detected_location = self.unit.detect(env, enemy_force)
        self.detected_location = detected_location
        return detected_location
    
    def createEvents(self, env, enemy_force):
        order_decided = False
        print(self.detected_location)
        if len(self.detected_location) > 0:
            print('checking distances')
            in_range = 0
            for M in self.unit.member:
                for i in np.arange(0, len(self.detected_location)):
                    dist = np.sqrt((M.location[0] - self.detected_location[i][0])**2 + (M.location[1] - self.detected_location[i][1])**2)
                    if dist < M.effective_range:
                        in_range += 1
            hold_prob = 0.1 * in_range
            random_sample = np.random.uniform()
            if random_sample < hold_prob:
                current_order = order.Hold()
                order_decided = True
        if order_decided == False:
            current_sector = False
            i = 0
            while current_sector == False:
                if self.achieved[i] == False:
                    for M in self.unit.member:
                        dist = np.sqrt((M.location[0] - self.sector_loc[self.assigned[i]][0])**2 + (M.location[1] - self.sector_loc[self.assigned[i]][1])**2)
                        if dist < 7.5:
                            self.achieved[i] = True
                if self.achieved[i] == False:
                    current_sector = True
                    current_order = order.MoveTo(self.sector_loc[self.assigned[i]])
                else:
                    i += 1
                if i == len(self.achieved)-1:
                    current_sector = True
                    current_order = order.MoveTo(self.sector_loc[self.assigned[i]])
        self.unit.setOrder(current_order)
        [manID, eventType, eventData] = self.unit.createEvents(env, enemy_force)
        sectionID = [self.sectionID] * len(manID)
        return [sectionID, manID, eventType, eventData]