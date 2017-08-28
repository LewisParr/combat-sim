# -*- coding: utf-8 -*-
# commander.py

import unit
import order
import objective
import company
import sector
import zone

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class TopLevelCommander(object):
    """
    TopLevelCommander provides an interface for the commanders most senior in
    the friendly and enemy forces.
    """
    def __init__(self, forceID, parameters, mission_objective):
        self.forceID = forceID
        if self.forceID == 0:
            self.enemy_forceID = 1
        else:
            self.enemy_forceID = 0
        self.objective = mission_objective
        # Set commander parameters
        # parameters: 0 - cwCover
        #             1 - cwConceal
        #             2 - cwVis
        #             3 - cwEnemyFOBProx
        #             4 - cwMissObjProx
        #             5 - pwFriendlyFOBProx
        #             6 - pwEnemyFOBProx
        #             7 - pwMissObjProx
        #             8 - company_parameters
        self.cwCover = parameters[0]
        self.cwConceal = parameters[1]
        self.cwVis = parameters[2]
        self.cwEnemyFOBProx = parameters[3]
        self.cwMissObjProx = parameters[4]
        self.pwFriendlyFOBProx = parameters[5]
        self.pwEnemyFOBProx = parameters[6]
        self.pwMissObjProx = parameters[7]
        self.company_parameters = parameters[8]
        # Initialise lists
        self.active_assets = []
        self.visible_area = []
        self.detected_enemy_assets = []
    
    def assignZones(self, env, enemy_fob_loc):
        # Set wUnitID by parameter later
        wUnitID = {2 : 1.0,
                   7 : 1.0}
        # Divide the environment into N zones, where N is the number of
        # companies available, and assign a zone to each.
        # 
        # Consider the cost of taking each sector, priority of each sector, 
        # and the capability of each company.
        sector_size = 10
        self.sector_size = sector_size
        nX = env.nX / sector_size
        nY = env.nY / sector_size
        self.sector = []
        self.cost = []
        self.priority = []
        self.ctr = []
        for x in np.arange(0, nX):
            x_min = x * sector_size
            x_max = ((x + 1) * sector_size)
            x_bounds = [x_min, x_max]
            sector_strip = []
            cost_strip = []
            priority_strip = []
            ctr_strip = []
            for y in np.arange(0, nY):
                y_min = y * sector_size
                y_max = ((y + 1) * sector_size)
                y_bounds = [y_min, y_max]
                bounds = x_bounds + y_bounds
                sector_strip.append(sector.Sector(env, bounds, self.hq.member.location, enemy_fob_loc, self.objective.ctr))
                # Estimate the cost of each sector.
                # 
                # Consider the sector's cover, concealment, visibility, proximity to 
                # enemy fob, proximity to mission objective.
                sector_cost = sector_strip[-1].cost([self.cwCover, self.cwConceal, self.cwVis, self.cwEnemyFOBProx, self.cwMissObjProx])
                cost_strip.append(sector_cost)
                # Estimate the priority of each sector.
                # 
                # Consider the sector's proximity to friendly fob, enemy fob, mission
                # objective.
                sector_priority = sector_strip[-1].priority([self.pwFriendlyFOBProx, self.pwEnemyFOBProx, self.pwMissObjProx])
                priority_strip.append(sector_priority)
                ctr_strip.append([np.mean(x_bounds), np.mean(y_bounds)])
            self.sector.append(sector_strip)
            self.cost.append(cost_strip)
            self.priority.append(priority_strip)
            self.ctr.append(ctr_strip)
        # Estimate the capability of each company.
        #
        # Weight the size of each section by the weight associated with its
        # unit type.
        self.capability = []
        for c in np.arange(0, len(self.company)):
            company_capability = 0
            for P in self.company[c].platoon:
                for S in P.section:
                    unitID = S.unit.unitID
                    w = wUnitID[unitID]
                    n = 0
                    for M in S.unit.member:
                        if M.status == 0:
                            n += 1
                    company_capability += w * n
            self.capability.append(company_capability)
        # Divide the sectors between the companies.
        # 
        # Consider the costs, priorities, capabilities.
        self.optimise_zones(env.nX, env.nY)

    def optimise_zones(self, nX, nY):
        # Assign a company value to each sector so that the variance in the sum
        # of cost per capability, sum of priority per capability, and distance
        # are minimised in solution.
#        nSectors = (nX / self.sector_size) * (nY / self.sector_size)
#        pop = zone.Population(nSectors, len(self.company), size=20)
#        best = []
#        for g in np.arange(0, 50):
#            pop.generation(len(self.company), nX, nY, self.cost, self.priority, self.capability, self.ctr)
#            best.append(pop.best_cost(len(self.company), nX, nY, self.cost, self.priority, self.capability, self.ctr))
#        sol = zone.Solution()
#        sol.layer(nX, nY, len(self.company))
#        sol.random(nSectors, len(self.company))
#        cost = sol.test(len(self.company), nX, nY, self.cost, self.priority, self.capability, self.ctr)

#        sol = zone.Solution()
#        sol.random(nX, nY, len(self.company))
#        sol.solve(self.cost, self.priority, self.capability, self.ctr)
#        assignment = sol.output(nX, nY)
#        
#        X, Y = np.meshgrid(np.arange(0, nX / 10), np.arange(0, nY / 10))
#        Z = assignment
#        plt.figure()
#        plt.contourf(X, Y, Z)
#        plt.show()
        
#        for i in np.arange(0, 9999):
#            new_assignment = sol.change(nSectors, len(self.company))
#            new_sol = zone.Solution()
#            new_sol.create(new_assignment)
##            for j in np.arange(0, 3):
##                new_sol.flip(len(self.company), nX, nY, self.ctr)
#            new_cost = new_sol.test(len(self.company), nX, nY, self.cost, self.priority, self.capability, self.ctr)
#            if new_cost < cost:
#                sol = new_sol
#                cost = new_cost
#            best.append(cost)
#            
#            if np.mod(i, 100) == 0:
#                X, Y = np.meshgrid(np.arange(0, nX / 10), np.arange(0, nY / 10))
#                Z = sol.assignment.reshape((int(nX) / 10, int(nY) / 10))
#                plt.figure()
#                plt.contourf(X, Y, Z)
#                plt.show()
            
#        plt.figure()
#        plt.plot(best)
#        plt.xlabel('Generation')
#        plt.ylabel('Solution Cost')
#        plt.title('Best Performing Solution')
#        plt.show()
#        best_solution = pop.select_best(len(self.company), nX, nY, self.cost, self.priority, self.capability, self.ctr)
#        best_solution = sol.output(nX, nY)
#        self.assignment = best_solution
        
        fob_loc = self.hq.member.location
        mo_loc = self.objective.ctr
        m = (fob_loc[1] - mo_loc[1]) / (fob_loc[0] - mo_loc[0])
        c = fob_loc[1] - (m * fob_loc[0])
        assignment = []
        for x in np.arange(0, len(self.sector)):
            assign_strip = []
            for y in np.arange(0, len(self.sector[x])):
                Y = (m * self.ctr[x][y][0]) + c
                if self.ctr[x][y][1] < Y:
                    assign_strip.append(0)
                else:
                    assign_strip.append(1)
            assignment.append(assign_strip)
        self.assignment = assignment
            
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
    
    def end_simulation(self):
        for C in self.company:
            C.order_history.append([C.order, C.order_duration])
            for P in C.platoon:
                P.order_history.append([P.order, P.order_duration])
                for S in P.section:
                    S.order_history.append([S.order, S.order_duration])
        
    def assignAssets(self, assets):
        self.hq = unit.Headquarters()
        nCompany = len(assets)
        self.company = []
        for C in np.arange(0, nCompany):
            self.company.append(company.CompanyCommander(C, assets[C], self.company_parameters))
        self.assigned_objective = [None] * nCompany
    
    def assignAssetLocations(self, locations, fob_location):
        self.hq.setLocation(fob_location)
        for C in np.arange(0, len(self.company)):
            for P in np.arange(0, len(self.company[C].platoon)):
                for S in np.arange(0, len(self.company[C].platoon[P].section)):
                    self.company[C].platoon[P].section[S].setLocation(locations[C][P][S])
    
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
    
    def calculateAttritionRate(self):
        attrition_rate = [0]
        for i in np.arange(1, len(self.active_assets)):
            attrition_rate.append((self.active_assets[i] - self.active_assets[i-1]) / 1) # CHANGE 1 TO LENGTH OF A TIMESTEP
        return attrition_rate
    
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
    
    def record_positions(self):
        for C in self.company:
            for P in C.platoon:
                for S in P.section:
                    for M in S.unit.member:
                        M.record_position()