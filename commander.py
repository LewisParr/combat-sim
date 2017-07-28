# -*- coding: utf-8 -*-
# commander.py

import unit
import order
import objective

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches

unitIDs = {2 : unit.Infantry,
           7 : unit.Sniper}

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
    def __init__(self, forceID):
        self.forceID = forceID
        if self.forceID == 0:
            self.enemy_forceID = 1
        else:
            self.enemy_forceID = 0
    
    def assignObjective(self, objective):
        self.objective = objective
        self.obj_graph = nx.DiGraph()
        self.obj_graph.add_node(self.objective)
        
    def assignAssets(self, assets):
        nCompany = len(assets)
        self.company = []
        for C in np.arange(0, nCompany):
            self.company.append(CompanyCommander(C, assets[C]))
    
    def assignAssetLocations(self, locations):
        for C in np.arange(0, len(self.company)):
            for P in np.arange(0, len(self.company[C].platoon)):
                for S in np.arange(0, len(self.company[C].platoon[P].section)):
                    self.company[C].platoon[P].section[S].setLocation(locations[C][P][S])

    def decomposeObjective(self, obj, env, expand=1):
        """
        ...
        """
        depth = 3
        print(obj.type)
        # Identify threats to objective
        [x, y] = obj.identifyThreats(env)
        # Create new objectives for countering identified threats
        threat_rect = []
        for a in np.arange(0, len(x)):
            NW = [env.visibility_cell[x[a]][y[a]].x_ctr - (env.visibility_cell_width / 2), env.visibility_cell[x[a]][y[a]].y_ctr + (env.visibility_cell_width / 2)]
            SE = [env.visibility_cell[x[a]][y[a]].x_ctr + (env.visibility_cell_width / 2), env.visibility_cell[x[a]][y[a]].y_ctr - (env.visibility_cell_width / 2)]
            new_obj = objective.ThreatArea(NW, SE)
            self.obj_graph.add_node(new_obj)
            self.obj_graph.add_edge(obj, new_obj)
            threat_rect.append(patches.Rectangle((NW[0], SE[1]), SE[0] - NW[0], NW[1] - SE[1], ec='r', fc='none'))
        # Plot objective and threats
        plt.figure()
        ax1 = plt.subplot(111)
        X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
        Z = env.getTerrainCellElevations()
        plt.contourf(X, Y, Z)
        obj_rect = patches.Rectangle((obj.NW[0], obj.SE[1]), obj.SE[0] - obj.NW[0], obj.NW[1] - obj.SE[1], ec='w', fc='none')
        for t_r in threat_rect:
            ax1.add_patch(t_r)
        ax1.add_patch(obj_rect)
        # Plot objective graph
        plt.figure()
        nx.draw(self.obj_graph)
        plt.show()
        # Expand new objectives if required
        if expand < depth:
            for s in self.obj_graph.successors(obj):
                self.decomposeObjective(s, env, expand=expand+1)
    
    def assignAssetObjectives(self):
        """
        Assigns the largest subordinate assets to objectives according to the
        objective graph (obj_graph) generated in objective decomposition.
        """
        # Find number of available assets
        a = 0
        for C in self.company:
            a += 1
        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(self.obj_graph, self, self.objective, a)
        # Assign assets to objectives
        i = 0
        for n in self.obj_graph.successors_iter(self.objective):
            self.obj_graph.node[n]['Owner'] = c[i]
            i += 1
        # Assign assets to subordinate objectives
        for n in self.obj_graph.successors_iter(self.objective):
            self.company[self.obj_graph.node[n]['Owner']].assignAssetObjectives(self.obj_graph, n)
    
    def giveOrders(self):
        """
        ...
        """
        for C in self.company:
            C.getOrder(order.MoveTo([200, 200]))
    
    def detect(self, env, enemy_force):
        detected_location = []
        for C in self.company:
            detected_location.append(C.detect(env, enemy_force))
        # CONSIDER DETECTED LOCATIONS IN LOGIC
    
    def createEvents(self, env, enemy_force):
        all_companyID = []
        all_platoonID = []
        all_sectionID = []
        all_manID = []
        all_eventType = []
        all_eventData = []
        for C in self.company:
            [companyID, platoonID, sectionID, manID, eventType, eventData] = C.createEvents(env, enemy_force)
            all_companyID.append(companyID)
            all_platoonID.append(platoonID)
            all_sectionID.append(sectionID)
            all_manID.append(manID)
            all_eventType.append(eventType)
            all_eventData.append(eventData)
        forceID = [self.forceID] * len(all_companyID)
        return [forceID, all_companyID, all_platoonID, all_sectionID, all_manID, all_eventType, all_eventData]
            
    def applyEvents(self):
        for C in self.company:
            C.applyEvents()
           
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
    def __init__(self, sectionID, unitID=2):
        self.sectionID = sectionID
        self.unit = unitIDs[unitID]()
        self.detected_location = []
    
    def setLocation(self, location):
        """
        location = [x, y] coordinates of section.
        """
        self.location = location
        self.unit.setLocation(location)
    
    def getOrder(self, order):
        """
        ...
        """
        self.order = order
        # Check detected locations here
        # Perform SA, etc here
        self.unit.setOrder(order)
    
    def detect(self, env, enemy_force):
        detected_location = self.unit.detect(env, enemy_force)
        self.detected_location = detected_location
        return detected_location
    
    def createEvents(self, env, enemy_force):
        """
        ...
        """
        [manID, eventType, eventData] = self.unit.createEvents(env, enemy_force)
        sectionID = [self.sectionID] * len(manID)
        return [sectionID, manID, eventType, eventData]

class PlatoonCommander(Commander):
    """
    PlatoonCommander handles the receiving of information from members of the
    platoon and communicates information to and from superior and inferior
    commanders.
    """
    def __init__(self, platoonID, assets):
        self.platoonID = platoonID
        nSection = assets
        self.section = []
        for S in np.arange(0, nSection):
            self.section.append(SectionCommander(S))
    
    def assignAssetObjectives(self, obj_graph, obj):
        """
        ...
        """
        # Find number of available assets
        a = 0
        for C in self.section:
            a += 1
        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(obj_graph, self, obj, a)
        # Assign assets to objectives
        i = 0
        for n in obj_graph.successors_iter(obj):
            obj_graph.node[n]['Owner'] = c[i]
            i += 1
    
    def getOrder(self, order):
        """
        ...
        """
        self.order = order
        self.giveOrders()
    
    def giveOrders(self):
        """
        ...
        """
        for S in self.section:
            S.getOrder(self.order)
    
    def detect(self, env, enemy_force):
        detected_location = []
        for S in self.section:
            detected_location.append(S.detect(env, enemy_force))
        # CONSIDER DETECTED LOCATIONS IN LOGIC
        return detected_location
    
    def createEvents(self, env, enemy_force):
        """
        ...
        """
        all_sectionID = []
        all_manID = []
        all_eventType = []
        all_eventData = []
        for S in self.section:
            [sectionID, manID, eventType, eventData] = S.createEvents(env, enemy_force)
            all_sectionID.append(sectionID)
            all_manID.append(manID)
            all_eventType.append(eventType)
            all_eventData.append(eventData)
        platoonID = [self.platoonID] * len(all_sectionID)
        return [platoonID, all_sectionID, all_manID, all_eventType, all_eventData]

class CompanyCommander(Commander):
    """
    CompanyCommander handles the receiving of information from members of the 
    company and communicates information to and from superior and inferior 
    commanders.
    """
    def __init__(self, companyID, assets):
        self.companyID = companyID
        nPlatoon = len(assets)
        self.platoon = []
        for P in np.arange(0, nPlatoon):
            self.platoon.append(PlatoonCommander(P, assets[P]))
    
    def assignAssetObjectives(self, obj_graph, obj):
        """
        ...
        """
        # Find number of available assets
        a = 0
        for C in self.platoon:
            a += 1
        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(obj_graph, self, obj, a)
        # Assign assets to objectives
        i = 0
        for n in obj_graph.successors_iter(obj):
            obj_graph.node[n]['Owner'] = c[i]
            i += 1
        # Assign assets to subordinate objectives
        for n in obj_graph.successors_iter(obj):
            self.platoon[obj_graph.node[n]['Owner']].assignAssetObjectives(obj_graph, n)
    
    def getOrder(self, order):
        self.order = order
        self.giveOrders()
    
    def giveOrders(self):
        for P in self.platoon:
            P.getOrder(self.order)
    
    def detect(self, env, enemy_force):
        detected_location = []
        for P in self.platoon:
            detected_location.append(P.detect(env, enemy_force))
        # CONSIDER DETECTED LOCATIONS IN LOGIC
        return detected_location
    
    def createEvents(self, env, enemy_force):
        all_platoonID = []
        all_sectionID = []
        all_manID = []
        all_eventType = []
        all_eventData = []
        for P in self.platoon:
            [platoonID, sectionID, manID, eventType, eventData] = P.createEvents(env, enemy_force)
            all_platoonID.append(platoonID)
            all_sectionID.append(sectionID)
            all_manID.append(manID)
            all_eventType.append(eventType)
            all_eventData.append(eventData)
        companyID = [self.companyID] * len(all_platoonID)
        return [companyID, all_platoonID, all_sectionID, all_manID, all_eventType, all_eventData]

def assignAssetObjectives(obj_graph, asset, objective, subordinates):
    """
    For a given objective within the objective graph, assign its successive 
    objectives to the available subordinate units.
    """
    # Find the number of subobjectives
    s = 0
    for n in obj_graph.successors_iter(objective):
        s += 1
    #print('Number of subobjectives: %s' % s)
    # Find the location of each subobjective
    loc = []
    for n in obj_graph.successors_iter(objective):
        x_ctr = (n.NW[0] + n.SE[0]) / 2
        y_ctr = (n.NW[1] + n.SE[1]) / 2
        loc.append([x_ctr, y_ctr])
    #print('Locations: %s' % loc)
    if len(loc) < subordinates:
        print('Fewer threats than subordinates.')
        c = []
        b = 0
        for n in obj_graph.successors_iter(objective):
            c.append(b)
            b += 1
    else:
        # Divide into 'a' clusters
        # Get min and max values
        x_bound = [np.min(np.asarray(loc)[:,0]), np.max(np.asarray(loc)[:,0])]
        y_bound = [np.min(np.asarray(loc)[:,1]), np.max(np.asarray(loc)[:,1])]
        #print('X boundaries: %s' % x_bound)
        #print('Y boundaries: %s' % y_bound)
        # Generate initial means
        mean = []
        for i in np.arange(0, subordinates):
            mean.append([np.random.randint(x_bound[0], x_bound[1]+1), np.random.randint(y_bound[0], y_bound[1]+1)])
        #print('Initial means:')
        #print(mean)
        # Calculate distances
        c = []
        for i in np.arange(0, len(loc)):
            x_dist = np.asarray(mean)[:,0] - loc[i][0]
            y_dist = np.asarray(mean)[:,1] - loc[i][1]
            dist = np.sqrt(x_dist**2 + y_dist**2)
            #print('Distance to cluster means: %s' % dist)
            # Assign to cluster
            c.append(np.where(dist == np.min(dist))[0][0])
        #print('Cluster allocations: %s' % c)
        # Iterate
        for n in np.arange(0, 100):
            new_mean = []
            for i in np.arange(0, subordinates):
                c_loc = []
                for j in np.arange(0, len(c)):
                    if c[j] == i:
                        c_loc.append(loc[j])
                if len(c_loc) > 0:
                    new_mean.append([np.mean(np.asarray(c_loc)[:,0]), np.mean(np.asarray(c_loc)[:,1])])
                else:
                    new_mean.append([np.random.randint(x_bound[0], x_bound[1]+1), np.random.randint(y_bound[0], y_bound[1]+1)])
            mean = new_mean
            c = []
            for i in np.arange(0, len(loc)):
                x_dist = np.asarray(mean)[:,0] - loc[i][0]
                y_dist = np.asarray(mean)[:,1] - loc[i][1]
                dist = np.sqrt(x_dist**2 + y_dist**2)
                # Assign to cluster
                c.append(np.where(dist == np.min(dist))[0][0])
            #print('Cluster allocations: %s' % c)
    # Plot asset allocations
    plt.figure()
    for i in np.arange(0, subordinates):
        c_loc = []
        for j in np.arange(0, len(c)):
            if c[j] == i:
                c_loc.append(loc[j])
        if len(c_loc) > 0:
            plt.scatter(np.asarray(c_loc)[:,0], np.asarray(c_loc)[:,1])
    plt.show()
    return c