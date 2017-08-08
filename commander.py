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
    def __init__(self, forceID, parameters):
        self.forceID = forceID
        if self.forceID == 0:
            self.enemy_forceID = 1
        else:
            self.enemy_forceID = 0
        # Set commander parameters
        self.mission_obj_weight = parameters[0]
        self.priority_decay = parameters[1]
        self.friendly_fob_weight = parameters[2]
        self.spatial_influence_weight = parameters[3]
        self.visibility_influence_weight = parameters[4]
        self.enemy_fob_weight = parameters[5]
        self.enemy_threat_weight = parameters[6]
        self.control_threshold = parameters[7]
        self.priority_cutoff = parameters[8]
        # Initialise lists
        self.active_assets = []
        self.visible_area = []
        self.detected_enemy_assets = []
    
    def end_simulation(self):
        for C in self.company:
            C.order_history.append([C.order, C.order_duration])
            for P in C.platoon:
                P.order_history.append([P.order, P.order_duration])
                for S in P.section:
                    S.order_history.append([S.order, S.order_duration])
    
    def assignObjective(self, objective):
        self.objective = objective
        self.obj_graph = nx.DiGraph()
        self.obj_graph.add_node(self.objective)
        
    def assignAssets(self, assets):
        self.hq = unit.Headquarters()
        nCompany = len(assets)
        self.company = []
        for C in np.arange(0, nCompany):
            self.company.append(CompanyCommander(C, assets[C]))
        self.assigned_objective = [None] * nCompany
    
    def assignAssetLocations(self, locations, fob_location):
        self.hq.setLocation(fob_location)
        for C in np.arange(0, len(self.company)):
            for P in np.arange(0, len(self.company[C].platoon)):
                for S in np.arange(0, len(self.company[C].platoon[P].section)):
                    self.company[C].platoon[P].section[S].setLocation(locations[C][P][S])

    def decomposeObjective(self, obj, env, expand=1):
        """
        ...
        """
        depth = 3
        # Identify threats to objective
        [x, y] = obj.identifyThreats(env)
        # Create new objectives for countering identified threats
#        threat_rect = []
        for a in np.arange(0, len(x)):
            NW = [env.visibility_cell[x[a]][y[a]].x_ctr - (env.visibility_cell_width / 2), env.visibility_cell[x[a]][y[a]].y_ctr + (env.visibility_cell_width / 2)]
            SE = [env.visibility_cell[x[a]][y[a]].x_ctr + (env.visibility_cell_width / 2), env.visibility_cell[x[a]][y[a]].y_ctr - (env.visibility_cell_width / 2)]
            new_obj = objective.ThreatArea(NW, SE)
            self.obj_graph.add_node(new_obj)
            self.obj_graph.add_edge(obj, new_obj)
#            threat_rect.append(patches.Rectangle((NW[0], SE[1]), SE[0] - NW[0], NW[1] - SE[1], ec='r', fc='none'))
        # Plot objective and threats
#        plt.figure()
#        ax1 = plt.subplot(111)
#        X, Y = np.meshgrid(np.arange(0, env.nX), np.arange(0, env.nY))
#        Z = env.getTerrainCellElevations()
#        plt.contourf(X, Y, Z)
#        obj_rect = patches.Rectangle((obj.NW[0], obj.SE[1]), obj.SE[0] - obj.NW[0], obj.NW[1] - obj.SE[1], ec='w', fc='none')
#        for t_r in threat_rect:
#            ax1.add_patch(t_r)
#        ax1.add_patch(obj_rect)
#        plt.show()
        # Plot objective graph
#        plt.figure()
#        nx.draw(self.obj_graph)
#        plt.show()
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
#        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(self.obj_graph, self, self.objective, a)
        # Assign assets to objectives
        i = 0
        for n in self.obj_graph.successors_iter(self.objective):
            self.obj_graph.node[n]['Owner'] = c[i]
            i += 1
        # Assign assets to subordinate objectives
        for n in self.obj_graph.successors_iter(self.objective):
            self.company[self.obj_graph.node[n]['Owner']].assignAssetObjectives(self.obj_graph, n)
    
    def updateObjectiveStatus(self, env, enemy_fob_location):
        parent_obj_x_ctr = ((self.objective.NW[0] + self.objective.SE[0]) / 2)
        parent_obj_y_ctr = ((self.objective.NW[1] + self.objective.SE[1]) / 2)
        for n in self.obj_graph.nodes_iter():
            obj_x_ctr = ((n.NW[0] + n.SE[0]) / 2)
            obj_y_ctr = ((n.NW[1] + n.SE[1]) / 2)
            # Determine objective priority
            dist = np.sqrt((obj_x_ctr - parent_obj_x_ctr)**2 + (obj_y_ctr - parent_obj_y_ctr)**2)
            self.obj_graph.node[n]['Priority'] = (1 * (self.priority_decay**nx.shortest_path_length(self.obj_graph, source=self.objective, target=n))) / (dist * self.mission_obj_weight)
            # Measure friendly influence over each objective (spatial proximity & visibility)
            spatial_influence = 0
            for C in self.company:
                for P in C.platoon:
                    for S in P.section:
                        for M in S.unit.member:
                            dist = np.sqrt((M.location[0] - obj_x_ctr)**2 + (M.location[1] - obj_y_ctr)**2)
                            spatial_influence += 1 / dist
            dist = np.sqrt((self.hq.member.location[0] - obj_x_ctr)**2 + (self.hq.member.location[1] - obj_y_ctr)**2)
            spatial_influence += self.friendly_fob_weight / dist
            v_maps = []
            for C in self.company:
                for P in C.platoon:
                    for S in P.section:
                        for M in S.unit.member:
                            cell_x = int(np.floor(M.location[0] / env.visibility_cell_width))
                            cell_y = int(np.floor(M.location[1] / env.visibility_cell_width))
                            v_maps.append(np.asarray(env.visibility_cell[cell_x][cell_y].v_map))
            v_map_all = v_maps[0]
            for i in np.arange(1, len(v_maps)):
                v_map_all = np.maximum(v_map_all, v_maps[i])
            visibility_influence = 0
            for x in np.arange(0, len(v_map_all)):
                for y in np.arange(0, len(v_map_all[x])):
                    x_ctr = env.visibility_cell[x][y].x_ctr
                    y_ctr = env.visibility_cell[x][y].y_ctr
                    dist = np.sqrt((obj_x_ctr - x_ctr)**2 + (obj_y_ctr - y_ctr)**2)
                    if dist == 0:
                        dist = 1
                    visibility_influence += v_map_all[x][y] / dist
            self.obj_graph.node[n]['Friendly Influence'] = (spatial_influence * self.spatial_influence_weight) + (visibility_influence * self.visibility_influence_weight)
            # Measure enemy threat to each objective
            enemy_threat = 0
            for l in self.detected_location:
                dist = np.sqrt((obj_x_ctr - l[0])**2 + (obj_y_ctr - l[1])**2)
                if dist == 0:
                    dist = 1
                enemy_threat += 1 / dist
            dist = np.sqrt((enemy_fob_location[0] - obj_x_ctr)**2 + (enemy_fob_location[1] - obj_y_ctr)**2)
            enemy_threat += self.enemy_fob_weight / dist
            self.obj_graph.node[n]['Enemy Threat'] = enemy_threat * self.enemy_threat_weight
            # Determine if objective needs to be taken/requires a stationed unit/can be left unattended
            if self.obj_graph.node[n]['Friendly Influence'] / self.obj_graph.node[n]['Enemy Threat'] > self.control_threshold:
                self.obj_graph.node[n]['Status'] = 'FRIENDLY'
            else:
                self.obj_graph.node[n]['Status'] = 'ADVERSARY'
    
    def giveOrders(self, env):
        # Calculate the prerequisite ratio for each objective to be assigned
        prereq = []
        for n in self.obj_graph.successors_iter(self.objective):
            nSuccessors = 0
            for o in self.obj_graph.successors_iter(n):
                nSuccessors += 1
            if nSuccessors > 0:
                nFriendly = 0
                for o in self.obj_graph.successors_iter(n):
                    if self.obj_graph.node[o]['Status'] == 'FRIENDLY':
                        nFriendly += 1
                prereq_ratio = nFriendly / nSuccessors
            else:
                prereq_ratio = 1.0
            prereq.append(prereq_ratio)
        # Calculate the assignment weight of each objective to be assigned
        counter = 0
        assignment_weight = []
        all_priority = []
        for n in self.obj_graph.successors_iter(self.objective):
            prereq_ratio = prereq[counter]
            if prereq_ratio == 0:
                prereq_ratio = 0.001
            counter += 1
            priority = self.obj_graph.node[n]['Priority']
            all_priority.append(priority)
            assignment_weight.append(priority / prereq_ratio)
        cum_assignment_weight = [assignment_weight[0]]
        for i in np.arange(1, len(assignment_weight)):
            cum_assignment_weight.append(cum_assignment_weight[-1] + assignment_weight[i])
        selection_weight = np.asarray(cum_assignment_weight) / cum_assignment_weight[-1]
        # Select objective and assign order to each subordinate asset
        mean_priority = np.mean(all_priority)
        for j in np.arange(0, len(self.company)):
            # Check if a new order is needed
            current_order = self.assigned_objective[j]
            if current_order != None:
                current_priority = self.obj_graph.node[current_order]['Priority']
                if current_priority < (self.priority_cutoff * mean_priority):
                    self.assignSubordinate(j, chooseObjective(selection_weight), self.obj_graph, self.objective, env)
                else:
                    self.company[j].getOrder(None, self.obj_graph, current_order, env)
            else:
                self.assignSubordinate(j, chooseObjective(selection_weight), self.obj_graph, self.objective, env)
                                   
    def assignSubordinate(self, companyID, selection, obj_graph, objective, env):
        counter = 0
        for n in obj_graph.successors_iter(objective):
            if counter == selection:
                chosen_objective = n
            counter += 1
        # Translate the chosen objective to an order
        x_ctr = (chosen_objective.NW[0] + chosen_objective.SE[0]) / 2
        y_ctr = (chosen_objective.NW[1] + chosen_objective.SE[1]) / 2
        self.company[companyID].getOrder(order.MoveTo([x_ctr, y_ctr]), obj_graph, chosen_objective, env)
        self.assigned_objective[companyID] = chosen_objective
            
    def detect(self, env, enemy_force):
        detected_location = []
        for C in self.company:
            detected_location.append(C.detect(env, enemy_force))
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
        self.detected_location = unique_detected_location
    
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
    
    def countActive(self):
        count = 0
        for C in self.company:
            for P in C.platoon:
                for S in P.section:
                    for M in S.unit.member:
                        if M.status == 0:
                            count += 1
        return count
    
    def measureVisibleArea(self, env):
        # Collate the areas visible by each asset
        v_maps = []
        for C in self.company:
            for P in C.platoon:
                for S in P.section:
                    for M in S.unit.member:
                        if M.status != 2:
                            cell_x = int(np.floor(M.location[0] / env.visibility_cell_width))
                            cell_y = int(np.floor(M.location[1] / env.visibility_cell_width))
                            v_maps.append(np.asarray(env.visibility_cell[cell_x][cell_y].v_map))
        if len(v_maps) > 0:
            v_map_all = v_maps[0]
            if len(v_maps) > 1:
                for i in np.arange(1, len(v_maps)):
                    v_map_all = np.maximum(v_map_all, v_maps[i])
            return np.sum(v_map_all) / ((env.nX * env.nY) / (env.visibility_cell_width**2)) # Percentage of environment visible (where visibility of a cell can take a fractional value)
        else:
            return 0.0
    
    def countDetected(self):
        return len(self.detected_location)
    
    def record(self, env):
        # Save the number of active assets
        self.active_assets.append(self.countActive())
        # Save the area of visibly terrain
        self.visible_area.append(self.measureVisibleArea(env))
        # Save the number of detected enemy assets
        self.detected_enemy_assets.append(self.countDetected())
           
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
        self.order = None
        self.order_history = []
        self.order_duration = 0
    
    def setLocation(self, location):
        """
        location = [x, y] coordinates of section.
        """
        self.location = location
        self.unit.setLocation(location)
    
    def getOrder(self, Order, env):
        if Order != None:
            self.order_history.append([self.order, self.order_duration])
            self.order = Order
            self.order_duration = 1
        else:
            self.order_duration += 1
        SA()
        # Calculate threat of each detected enemy to each friendly member
        # For now, use visibility as threat measure (0 if outside effective range)
        enemy_threat = []
        for a in np.arange(0, len(self.detected_location)):
            enemy_cell_x = int(np.floor(self.detected_location[a][0] / env.visibility_cell_width))
            enemy_cell_y = int(np.floor(self.detected_location[a][1] / env.visibility_cell_width))
            ind_enemy_threat = []
            for b in np.arange(0, len(self.unit.member)):
                cell_x = int(np.floor(self.unit.member[b].location[0] / env.visibility_cell_width))
                cell_y = int(np.floor(self.unit.member[b].location[1] / env.visibility_cell_width))
                if np.sqrt((self.unit.member[b].location[0] - self.detected_location[a][0])**2 + (self.unit.member[b].location[1] - self.detected_location[a][1])**2) < 50:
                    ind_enemy_threat.append(env.visibility_cell[enemy_cell_x][enemy_cell_y].v_map[cell_x][cell_y])
                else:
                    ind_enemy_threat.append(0)
            enemy_threat.append(ind_enemy_threat)
        # Calculate threat of each friendly member to each detected enemy
        friendly_threat = []
        for a in np.arange(0, len(self.unit.member)):
            cell_x = int(np.floor(self.unit.member[a].location[0] / env.visibility_cell_width))
            cell_y = int(np.floor(self.unit.member[a].location[1] / env.visibility_cell_width))
            ind_friendly_threat = []
            for b in np.arange(0, len(self.detected_location)):
                enemy_cell_x = int(np.floor(self.detected_location[b][0] / env.visibility_cell_width))
                enemy_cell_y = int(np.floor(self.detected_location[b][1] / env.visibility_cell_width))
                if np.sqrt((self.detected_location[b][0] - self.unit.member[a].location[0])**2 + (self.detected_location[b][1] - self.unit.member[a].location[1])**2) < self.unit.member[a].effective_range:
                    ind_friendly_threat.append(env.visibility_cell[cell_x][cell_y].v_map[enemy_cell_x][enemy_cell_y])
                else:
                    ind_friendly_threat.append(0)
            friendly_threat.append(ind_friendly_threat)
        # Calculate threat ratio of each detected enemy
        enemy_threat_ratio = []
        for a in np.arange(0, len(enemy_threat)):
            out_threat = np.sum(enemy_threat[a])
            in_threat = 0
            for b in np.arange(0, len(friendly_threat)):
                in_threat += friendly_threat[b][a]
            if in_threat != 0:
                enemy_threat_ratio.append(out_threat / in_threat)
            else:
                enemy_threat_ratio.append(out_threat)
        # Calculate threat ratio of each friendly member
        friendly_threat_ratio = []
        for a in np.arange(0, len(friendly_threat)):
            out_threat = np.sum(friendly_threat[a])
            in_threat = 0
            for b in np.arange(0, len(enemy_threat)):
                in_threat += enemy_threat[b][a]
            if in_threat != 0:
                friendly_threat_ratio.append(out_threat / in_threat)
            else:
                friendly_threat_ratio.append(out_threat)
        # Need to decide on logic for engaging, etc based on threat ratios
        # For now, if enemy is detected, order to hold position
        # Check detected locations here
        # Perform SA, etc here
        if np.mean(enemy_threat_ratio) > 0:
            self.unit.setOrder(order.Defend())
        else:
            self.unit.setOrder(Order)
        # Send order to defend if in location
    
    def detect(self, env, enemy_force):
        detected_location = self.unit.detect(env, enemy_force)
        self.detected_location = detected_location
        return detected_location
    
    def createEvents(self, env, enemy_force):
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
        self.assigned_objective = [None] * nSection
        self.order = None
        self.order_history = []
        self.order_duration = 0
    
    def assignAssetObjectives(self, obj_graph, obj):
        """
        ...
        """
        # Find number of available assets
        a = 0
        for C in self.section:
            a += 1
#        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(obj_graph, self, obj, a)
        # Assign assets to objectives
        i = 0
        for n in obj_graph.successors_iter(obj):
            obj_graph.node[n]['Owner'] = c[i]
            i += 1
    
    def getOrder(self, Order, obj_graph, objective, env):
        if Order != None:
            self.order_history.append([self.order, self.order_duration])
            self.order = Order
            self.order_duration = 1
        else:
            self.order_duration += 1
        self.giveOrders(obj_graph, objective, env)
    
    def giveOrders(self, obj_graph, objective, env):
        # Calculate the prerequisite ratio for each objective to be assigned
        prereq = []
        for n in obj_graph.successors_iter(objective):
            nSuccessors = 0
            for o in obj_graph.successors_iter(n):
                nSuccessors += 1
            if nSuccessors > 0:
                nFriendly = 0
                for o in obj_graph.successors_iter(n):
                    if obj_graph.node[o]['Status'] == 'FRIENDLY':
                        nFriendly += 1
                prereq_ratio = nFriendly / nSuccessors
            else:
                prereq_ratio = 1.0
            prereq.append(prereq_ratio)
        # Calculate the assignment weight of each objective to be assigned
        counter = 0
        assignment_weight = []
        all_priority = []
        for n in obj_graph.successors_iter(objective):
            prereq_ratio = prereq[counter]
            if prereq_ratio == 0:
                prereq_ratio = 0.001
            counter += 1
            priority = obj_graph.node[n]['Priority']
            all_priority.append(priority)
            assignment_weight.append(priority / prereq_ratio)
        if len(assignment_weight) > 0:
            cum_assignment_weight = [assignment_weight[0]]
            if len(assignment_weight) > 1:
                for i in np.arange(1, len(assignment_weight)):
                    cum_assignment_weight.append(cum_assignment_weight[-1] + assignment_weight[i])
            selection_weight = np.asarray(cum_assignment_weight) / cum_assignment_weight[-1]
            # Select objective and assign order to each subordinate asset
            mean_priority = np.mean(all_priority)
            for j in np.arange(0, len(self.section)):
                # Check if a new order is needed
                current_order = self.assigned_objective[j]
                if current_order != None:
                    current_priority = obj_graph.node[current_order]['Priority']
                    priority_cutoff = 0.75                                          # TO BE LEARNT BY COMMANDER
                    if current_priority < (priority_cutoff * mean_priority):
                        self.assignSubordinate(j, chooseObjective(selection_weight), obj_graph, objective, env)
                    else:
                        self.section[j].getOrder(None, env)
                else:
                    self.assignSubordinate(j, chooseObjective(selection_weight), obj_graph, objective, env)
            else:
                # Assign own order to each subordinate
                for j in np.arange(0, len(self.section)):
                    self.section[j].getOrder(self.order, env)
                    
    def assignSubordinate(self, sectionID, selection, obj_graph, objective, env):
        counter = 0
        for n in obj_graph.successors_iter(objective):
            if counter == selection:
                chosen_objective = n
            counter += 1
        # Translate the chosen objective to an order
        x_ctr = (chosen_objective.NW[0] + chosen_objective.SE[0]) / 2
        y_ctr = (chosen_objective.NW[1] + chosen_objective.SE[1]) / 2
        self.section[sectionID].getOrder(order.MoveTo([x_ctr, y_ctr]), env)
        self.assigned_objective[sectionID] = chosen_objective
                
    
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
        self.assigned_objective = [None] * nPlatoon
        self.order = None
        self.order_history = []
        self.order_duration = 0
    
    def assignAssetObjectives(self, obj_graph, obj):
        # Find number of available assets
        a = 0
        for C in self.platoon:
            a += 1
#        print('Number of available assets: %s' % a)
        c = assignAssetObjectives(obj_graph, self, obj, a)
        # Assign assets to objectives
        i = 0
        for n in obj_graph.successors_iter(obj):
            obj_graph.node[n]['Owner'] = c[i]
            i += 1
        # Assign assets to subordinate objectives
        for n in obj_graph.successors_iter(obj):
            self.platoon[obj_graph.node[n]['Owner']].assignAssetObjectives(obj_graph, n)
    
    def getOrder(self, Order, obj_graph, objective, env):
        if Order != None:
            self.order_history.append([self.order, self.order_duration])
            self.order = Order
            self.order_duration = 1
        else:
            self.order_duration += 1
        self.giveOrders(obj_graph, objective, env)
    
    def giveOrders(self, obj_graph, objective, env):
        # Calculate the prerequisite ratio for each objective to be assigned
        prereq = []
        for n in obj_graph.successors_iter(objective):
            nSuccessors = 0
            for o in obj_graph.successors_iter(n):
                nSuccessors += 1
            if nSuccessors > 0:
                nFriendly = 0
                for o in obj_graph.successors_iter(n):
                    if obj_graph.node[o]['Status'] == 'FRIENDLY':
                        nFriendly += 1
                prereq_ratio = nFriendly / nSuccessors
            else:
                prereq_ratio = 1.0
            prereq.append(prereq_ratio)
        # Calculate the assignment weight of each objective to be assigned
        counter = 0
        assignment_weight = []
        all_priority = []
        for n in obj_graph.successors_iter(objective):
            prereq_ratio = prereq[counter]
            if prereq_ratio == 0:
                prereq_ratio = 0.001
            counter += 1
            priority = obj_graph.node[n]['Priority']
            all_priority.append(priority)
            assignment_weight.append(priority / prereq_ratio)
        cum_assignment_weight = [assignment_weight[0]]
        for i in np.arange(1, len(assignment_weight)):
            cum_assignment_weight.append(cum_assignment_weight[-1] + assignment_weight[i])
        selection_weight = np.asarray(cum_assignment_weight) / cum_assignment_weight[-1]
        # Select objective and assign order to each subordinate asset
        mean_priority = np.mean(all_priority)
        for j in np.arange(0, len(self.platoon)):
            # Check if a new order is needed
            current_order = self.assigned_objective[j]
            if current_order != None:
                current_priority = obj_graph.node[current_order]['Priority']
                priority_cutoff = 0.75                                          # TO BE LEARNT BY COMMANDER
                if current_priority < (priority_cutoff * mean_priority):
                    self.assignSubordinate(j, chooseObjective(selection_weight), obj_graph, objective, env)
                else:
                    self.platoon[j].getOrder(None, obj_graph, current_order, env)
            else:
                self.assignSubordinate(j, chooseObjective(selection_weight), obj_graph, objective, env)

    def assignSubordinate(self, platoonID, selection, obj_graph, objective, env):
        counter = 0
        for n in obj_graph.successors_iter(objective):
            if counter == selection:
                chosen_objective = n
            counter += 1
        # Translate the chosen objective to an order
        x_ctr = (chosen_objective.NW[0] + chosen_objective.SE[0]) / 2
        y_ctr = (chosen_objective.NW[1] + chosen_objective.SE[1]) / 2
        self.platoon[platoonID].getOrder(order.MoveTo([x_ctr, y_ctr]), obj_graph, chosen_objective, env)
        self.assigned_objective[platoonID] = chosen_objective
    
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
    # Find the total number of subobjectives
    nSuccessors = []
    for n in obj_graph.successors_iter(objective):
        nSuccessors.append(countObjectiveSuccessors(obj_graph, n))
#    print(nSuccessors)
    # Find the location of each subobjective
    loc = []
    for n in obj_graph.successors_iter(objective):
        x_ctr = (n.NW[0] + n.SE[0]) / 2
        y_ctr = (n.NW[1] + n.SE[1]) / 2
        loc.append([x_ctr, y_ctr])
    #print('Locations: %s' % loc)
    if len(loc) < subordinates:
#        print('Fewer threats than subordinates.')
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
#    plt.figure()
#    for i in np.arange(0, subordinates):
#        c_loc = []
#        for j in np.arange(0, len(c)):
#            if c[j] == i:
#                c_loc.append(loc[j])
#        if len(c_loc) > 0:
#            plt.scatter(np.asarray(c_loc)[:,0], np.asarray(c_loc)[:,1])
#    plt.show()
    return c

def countObjectiveSuccessors(obj_graph, objective):
    """
    For a given objective, count the number of subordinate subobjectives.
    """
    nSuccessors = len(obj_graph.successors(objective))
    for n in obj_graph.successors_iter(objective):
        nSuccessors += countObjectiveSuccessors(obj_graph, n)
    return nSuccessors

def chooseObjective(selection_weight):
    # Select an objective to be assigned (with weights)
    random_sample = np.random.uniform(low=0.0, high=1.0)
    found = False
    i = 0
    if random_sample < selection_weight[0]:
        found = True
    else:
        while found == False:
            i += 1
            if random_sample > selection_weight[i-1]:
                if random_sample < selection_weight[i]:
                    found = True
    return i

def SA():
    """
    Inputs:
    - friendly locations
    - enemy locations
    - environment
    """
    # Perception
    # ...
    # Comprehension
    # ...
    # Projection
    # ...
    pass