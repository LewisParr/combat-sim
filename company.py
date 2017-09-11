# -*- coding: utf-8 -*-
# company.py

import platoon

import numpy as np
import networkx as nx

class CompanyCommander(object):
    """
    CompanyCommander handles the receiving of information from members of the 
    company and communicates information to and from superior and inferior 
    commanders.
    """
    def __init__(self, companyID, assets, parameters, speed):
        # [1.0, 1.0, 1.0, [30.0]]
        # parameters: 0 - ewDist
        #             1 - ewCover
        #             2 - ewConceal
        #             3 - platoon_parameters
        self.companyID = companyID
        self.ewDist = parameters[0]
        self.ewCover = parameters[1]
        self.ewConceal = parameters[2]
        dist_from_path = parameters[3]
        swHold = parameters[4]
        stMorale = parameters[5]
        self.platoon_parameters = [dist_from_path, swHold, stMorale]
        nPlatoon = len(assets)
        self.platoon = []
        for P in np.arange(0, nPlatoon):
            self.platoon.append(platoon.PlatoonCommander(P, assets[P], self.platoon_parameters, speed))
        self.assigned_objective = [None] * nPlatoon
        self.order = None
        self.order_history = []
        self.order_duration = 0
    
    def detect(self, env, enemy_force):
        detected_location = []
        for P in self.platoon:
            detected_location.append(P.detect(env, enemy_force))
        unique_detected_location = []
        for a in np.arange(0, len(detected_location)):
            for b in np.arange(0, len(detected_location[a])):
                x = detected_location[a][b][0]
                y = detected_location[a][b][1]
                found = False
                tol = 0.001
                for c in unique_detected_location:
                    if np.absolute(c[0] - x) < tol:
                        if np.absolute(c[1] - y) < tol:
                            found = True
                if found == False:
                    unique_detected_location.append(detected_location[a][b])
        return unique_detected_location
    
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
    
    def assignCOAPath(self, assignment, ctr, cost, priority, fob_loc, obj_loc, sector):
        # Set wUnitID by parameter later
        wUnitID = {2 : 1.0,
                   7 : 1.0}
#        sector = np.asarray(sector)
#        sector = sector.reshape((1, len(sector) * len(sector[0])))              # Depends on sector_size
#        sector = sector[0]
        # Collect assigned locations, node costs, node priorities
        loc = []
        sector_x = []
        sector_y = []
        node_cost = []
        node_priority = []
        for x in np.arange(0, len(assignment)):
            for y in np.arange(0, len(assignment[x])):
                if assignment[x][y] == self.companyID:
                    loc.append(ctr[x][y])
                    sector_x.append(x)
                    sector_y.append(y)
                    node_cost.append(cost[x][y])
                    node_priority.append(priority[x][y]) # X AND Y DO NOT IDENTIFY CORRECT SECTORS
        # Add friendly fob and mission objective
        loc.append(fob_loc)
        x = 0
        while fob_loc[0] > (x + 1) * 10:
            x += 1
        y = 0
        while fob_loc[1] > (y + 1) * 10:
            y += 1
        sector_x.append(x)
        sector_y.append(y)
        node_cost.append(0)
        node_priority.append(0)
        loc.append(obj_loc)
        x = 0
        while fob_loc[0] > (x + 1) * 10:
            x += 1
        y = 0
        while fob_loc[1] > (y + 1) * 10:
            y += 1
        sector_x.append(x)
        sector_y.append(y)
        node_cost.append(0)
        node_priority.append(0)
        # Build graph and create nodes
        AO = nx.Graph()
        for i in np.arange(0, len(loc)):
            AO.add_node(i)
            AO.node[i]['Location'] = loc[i]
            AO.node[i]['Cost'] = node_cost[i]
            AO.node[i]['Priority'] = node_priority[i]
            AO.node[i]['Available'] = True
        # Build distance matrix for assigned sectors
        dist = []
        for i in np.arange(0, len(loc)):
            dist_strip = []
            for j in np.arange(0, len(loc)):
                dist_strip.append(np.sqrt((loc[i][0] - loc[j][0])**2 + (loc[i][1] - loc[j][1])**2))
            dist.append(dist_strip)
        # Estimate edge costs
        edge_cost = []
        for i in np.arange(0, len(loc)):
            edge_cost_strip = []
            for j in np.arange(0, len(loc)):
                if i == j:
                    edge_cost_strip.append(0.0)
                else:
                    # ALSO NEED TO ADD COST FOR CROSSING SECTORS
                    edge_cost_strip.append((self.ewDist * dist[i][j]) + (self.ewCover * (sector[sector_x[i]][sector_y[i]].mean_cover + sector[sector_x[j]][sector_y[j]].mean_cover)) + (self.ewConceal * (sector[sector_x[i]][sector_y[i]].mean_conceal + sector[sector_x[j]][sector_y[j]].mean_conceal)))
            edge_cost.append(edge_cost_strip)
        # Create edges
        for i in np.arange(0, len(loc)):
            for j in np.arange(0, len(loc)):
                AO.add_edge(i, j)
                AO[i][j]['Cost'] = edge_cost[i][j]
        # Run variant of Dijkstra's algorithm
        [path, cost] = self.dijkstra_handler(AO, len(loc)-2, len(loc)-1)
        # Estimate the capability of each platoon    
        capability = []
        for P in self.platoon:
            platoon_capability = 0
            for S in P.section:
                unitID = S.unit.unitID
                w = wUnitID[unitID]
                n = 0
                for M in S.unit.member:
                    if M.status == 0:
                        n += 1
                platoon_capability += w * n
            capability.append(platoon_capability)
        # Assign paths to platoons
        platoon_num = np.arange(0, len(self.platoon))
        self.assignment = []
        for i in np.arange(0, len(self.platoon)):
            a = np.argmax(cost)
            b = np.argmax(capability)
            # USE PLATOON_NUM TO ADD TO ASSIGNMENT
            platoon_assignment = [path[a], cost[a]]
            self.assignment.append(platoon_assignment)
            path.pop(a)
            cost.pop(a)
            capability.pop(b)
        self.sector_loc = loc
#        self.sector_x = sector_x
#        self.sector_y = sector_y
        self.AO = AO
        # MEASURE SPREAD OF PATHS AND LEARN?
    
    def dijkstra_handler(self, graph, initial, final):
        # Find best
        path = []
        cost = []
        [best_path, best_cost] = dijkstra(graph, initial, final)
        path.append(best_path)
        cost.append(best_cost)
        # Find others
        for a in np.arange(1, len(self.platoon)):
            for i in path[-1]:
                if i != initial:
                    if i != final:
                        graph.node[i]['Available'] = False
            [best_path, best_cost] = dijkstra(graph, initial, final)
            path.append(best_path)
            cost.append(best_cost)
        return [path, cost]
                
    
def dijkstra(graph, initial, final):
    # Set tentative values
    unvisited = []
    for n in graph.nodes_iter():
        if n == initial:
            graph.node[n]['Tentative'] = 0.0
            graph.node[n]['Path'] = [n]
        else:
            graph.node[n]['Tentative'] = 999999.0
            graph.node[n]['Path'] = []
            unvisited.append(n)
    # Set the current node
    current = initial
    for n in graph.neighbors_iter(current):
        tentative = graph.node[current]['Tentative'] + ((graph[current][n]['Cost'] + graph.node[n]['Cost'] + 1.0) / (graph.node[n]['Priority'] + 1.0))
        if tentative < graph.node[n]['Tentative']:
            if graph.node[n]['Available'] == True:
                graph.node[n]['Tentative'] = tentative
                graph.node[n]['Path'] = graph.node[current]['Path'] + [n]
    # Find the unvisited node with the lowest tentative value
    tentative = []
    for n in unvisited:
        tentative.append(graph.node[n]['Tentative'])
    i = np.argmin(tentative)
    current = unvisited[i]
    unvisited.pop(i)
    # Repeat
    while final in unvisited:
        for n in graph.neighbors_iter(current):
            tentative = graph.node[current]['Tentative'] + ((graph[current][n]['Cost'] + graph.node[n]['Cost'] + 1.0) / (graph.node[n]['Priority'] + 1.0))
            if tentative < graph.node[n]['Tentative']:
                if graph.node[n]['Available'] == True:
                    graph.node[n]['Tentative'] = tentative
                    graph.node[n]['Path'] = graph.node[current]['Path'] + [n]
        tentative = []
        for n in unvisited:
            tentative.append(graph.node[n]['Tentative'])
        i = np.argmin(tentative)
        current = unvisited[i]
        unvisited.pop(i)
    best_path = graph.node[final]['Path']
    best_cost = graph.node[final]['Tentative']
    return [best_path, best_cost]