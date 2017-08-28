# -*- coding: utf-8 -*-
# sector.py

import numpy as np

class Sector(object):
    def __init__(self, env, bounds, friendly_fob_loc, enemy_fob_loc, mission_obj_loc):
        # Calculate mean cover, concealment, visibility
        count = 0
        cum_cover = 0
        cum_conceal = 0
        cum_visibility = 0
        cum_friendly_fob_dist = 0
        cum_enemy_fob_dist = 0
        cum_mission_obj_dist = 0
        for x in np.arange(bounds[0], bounds[1]):
            for y in np.arange(bounds[2], bounds[3]):
                count += 1
                cum_cover += env.terrain_cell[int(x)][int(y)].cover
                cum_conceal += env.terrain_cell[int(x)][int(y)].concealment
                cell_x = int(np.floor(x / env.visibility_cell_width))
                cell_y = int(np.floor(y / env.visibility_cell_width))
                cum_visibility += np.mean(env.visibility_cell[cell_x][cell_y].v_map) # DO SOMETHING WITH VISIBILITY
                cum_friendly_fob_dist += np.sqrt((friendly_fob_loc[0] - x)**2 + (friendly_fob_loc[1] - y)**2)
                cum_enemy_fob_dist += np.sqrt((enemy_fob_loc[0] - x)**2 + (enemy_fob_loc[1] - y)**2)
                cum_mission_obj_dist += np.sqrt((mission_obj_loc[0] - x)**2 + (mission_obj_loc[1] - y)**2)
        self.mean_cover = cum_cover / count
        self.mean_conceal = cum_conceal / count
        self.mean_friendly_fob_dist = cum_friendly_fob_dist / count
        self.mean_enemy_fob_dist = cum_enemy_fob_dist / count
        self.mean_mission_obj_dist = cum_mission_obj_dist / count
    
    def cost(self, weight):
        value = [self.mean_cover, self.mean_conceal, self.mean_enemy_fob_dist, self.mean_mission_obj_dist]
        cost = 0
        for i in np.arange(0, len(value)):
            cost += value[i] * weight[i]
        self.cost_est = cost
        return cost
    
    def priority(self, weight):
        value = [self.mean_friendly_fob_dist, self.mean_enemy_fob_dist, self.mean_mission_obj_dist]
        priority = 0
        for i in np.arange(0, len(value)):
            priority += value[i] * weight[i]
        self.priority_est = priority
        return priority