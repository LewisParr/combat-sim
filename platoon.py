# -*- coding: utf-8 -*-
# platoon.py

import section
import company

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class PlatoonCommander(object):
    """
    PlatoonCommander handles the receiving of information from members of the
    platoon and communicates information to and from superior and inferior
    commanders.
    """
    def __init__(self, platoonID, assets, parameters, speed):
        # parameters: 0 - dist_from_path
        #             1 - swHold
        self.platoonID = platoonID
        self.dist_from_path = parameters[0]
        self.swHold = parameters[1]
        self.stMorale = parameters[2]
        nSection = assets
        self.section = []
        for S in np.arange(0, nSection):
            self.section.append(section.SectionCommander(S, self.swHold, self.stMorale, speed))
        self.assigned_objective = [None] * nSection
        self.order = None
        self.order_history = []
        self.order_duration = 0
                
    
    def detect(self, env, enemy_force):
        detected_location = []
        for S in self.section:
            detected_location.append(S.detect(env, enemy_force))
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
    
    def assignCOAPath(self, assignment, graph, sector_loc):
        # Set wUnitID by parameter later
        wUnitID = {2 : 1.0,
                   7 : 1.0}
        # Find points along path
        assigned = assignment[self.platoonID][0] # CURRENTLY JUST ACCEPTS IN PLATOON ORDER
        x = []
        y = []
        for i in np.arange(0, len(assigned)-1):
            x_initial = sector_loc[assigned[i]][0]
            x_final = sector_loc[assigned[i+1]][0]
            y_initial = sector_loc[assigned[i]][1]
            y_final = sector_loc[assigned[i+1]][1]
            x_points = np.linspace(x_initial, x_final, num=100)
            y_points = np.linspace(y_initial, y_final, num=100)
            for j in np.arange(0, len(x_points)):
                x.append(x_points[j])
                y.append(y_points[j])
        # Remove sectors from graph that are outside range
        AO = graph.copy()
        remove = []
        location = []
        node = []
        
        all_x = []
        all_y = []
        saved_x = []
        saved_y = []
        
        for n in AO.nodes_iter():
            loc = AO.node[n]['Location']
            all_x.append(loc[0])
            all_y.append(loc[1])
            in_range = False
            for i in np.arange(0, len(x)):
                dist = np.sqrt((x[i] - loc[0])**2 + (y[i] - loc[1])**2)
                if dist < self.dist_from_path:
                    in_range = True
                    location.append(loc)
                    saved_x.append(loc[0])
                    saved_y.append(loc[1])
                    node.append(n)
            if in_range == False:
                remove.append(n)
#        plt.figure()
#        plt.scatter(all_x, all_y)
#        plt.scatter(saved_x, saved_y)
#        plt.xlabel('X (Sector)')
#        plt.ylabel('Y (Sector)')
#        plt.title('AO Nodes')
#        plt.show()
        AO.remove_nodes_from(remove)
        # Remove all edges from the graph that do not connect adjacent sectors
        remove = []
        for e in AO.edges_iter():
            locA = AO.node[e[0]]['Location']
            locB = AO.node[e[1]]['Location']
            dist = np.sqrt((locA[0] - locB[0])**2 + (locA[1] - locB[1])**2)
            if dist > 15.0:
                remove.append(e)
        AO.remove_edges_from(remove)
#        position_dict = dict(zip(node, location))
#        plot_Graph(AO, position_dict)
        # Use Dijkstra's algorithm variant to find best path
        [path, cost] = self.dijkstra_handler(AO, assigned)
        # Estimate the capability of each section
        capability = []
        for S in self.section:
            unitID = S.unit.unitID
            w = wUnitID[unitID]
            n = 0
            for M in S.unit.member:
                if M.status == 0:
                    n += 1
            capability.append(w * n)
        # Assign paths to sections
        self.assignment = []
        for i in np.arange(0, len(self.section)):
            a = np.argmax(cost)
            b = np.argmax(capability)
            # USE PLATOON_NUM TO ADD TO ASSIGNMENT
            section_assignment = [path[a], cost[a]]
            self.assignment.append(section_assignment)
            path.pop(a)
            cost.pop(a)
            capability.pop(b)
        self.sector_loc = sector_loc
        self.AO = AO

    def dijkstra_handler(self, graph, assigned):
        # Set all nodes to available
        for n in graph.nodes_iter():
            graph.node[n]['Available'] = True
        # Find best
        path = []
        cost = []
        [best_path, best_cost] = company.dijkstra(graph, assigned[0], assigned[-1])
        path.append(best_path)
        cost.append(best_cost)
        for a in np.arange(1, len(self.section)):
            for i in path[-1]:
                if i != assigned[0]:
                    if i != assigned[-1]:
                        graph.node[i]['Available'] = False
            [best_path, best_cost] = company.dijkstra(graph, assigned[0], assigned[-1])
            if best_cost == 999999.0:
                if len(path) > 0:
                    path.append(path[-1])
                    cost.append(cost[-1])
                else:
                    print('No possible path.')
                    path.append(best_path)
                    cost.append(best_cost)                    
            else:
                path.append(best_path)
                cost.append(best_cost)
        return [path, cost]

def plot_Graph(graph, position_dict):
    plt.figure()
    nx.draw(graph, pos=position_dict)
    plt.show()