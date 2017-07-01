# -*- coding: utf-8 -*-
"""
Two-Sided 2D Combat
"""

# Import libraries
import csv
import numpy as np
import matplotlib.pyplot as plt

# Scenario
scenario_id = 0
mission_objective = [['OCCUPY', [[-5, 5], [-5, 5]]], ['OCCUPY', [[-5, 5], [-5, 5]]]]
unit_count = [10, 10]
unit_loc1 = [[-90,-1000], [-70,-1000], [-50,-1000], [-30,-1000], [-10,-1000], [10,-1000], [30,-1000], [50,-1000], [70,-1000], [90,-1000]]
unit_loc2 = [[-90, 1000], [-70, 1000], [-50, 1000], [-30, 1000], [-10, 1000], [10, 1000], [30, 1000], [50, 1000], [70, 1000], [90, 1000]]
unit_loc = [unit_loc1, unit_loc2]

class Environment(object):
    def __init__(self):
        self.scenario_id = scenario_id
        self.t = 0
        self.com = []
        for i in np.arange(0, 2):
            self.com.append(Commander(i, unit_count[i], unit_loc[i], mission_objective[i]))
        self.score = [[self.com[0].countActive()], [self.com[0].countActive()]]
        self.move_event = []
        self.fire_event = []
        self.move_event_record = []
        self.fire_event_record = []
        self.move_x_source = []
        self.move_y_source = []
        self.move_x_new = []
        self.move_y_new = []
        self.fire_x_source = []
        self.fire_y_source = []
        self.fire_x_target = []
        self.fire_y_target = []
        self.defineZones()
    
    def plotScore(self):
        colour = ['b', 'r']
        plt.figure()
        for a in np.arange(0, 2):
            plt.plot(self.score[a], c=colour[a])
        plt.title('Score')
        plt.show()
    
    def plotLocations(self):
        colour = ['b', 'r']
        plt.figure()
        for a in np.arange(0, 2):
            for b in np.arange(0, len(self.com[a].ft)):
                [x, y] = self.com[a].ft[b].getLocs()
                plt.scatter(x, y, marker='.', c=colour[a])
            [x, y] = self.com[a].getLocs()
            #plt.scatter(x, y, marker='x', c=colour[a])
        plt.title('Locations')
        plt.show()
        
    def plotMovements(self):
        for i in np.arange(0, len(self.move_event)):
            source = self.move_event[i].source
            self.move_x_source.append(self.com[source[0]].ft[source[1]].man[source[2]].loc[0])
            self.move_y_source.append(self.com[source[0]].ft[source[1]].man[source[2]].loc[1])
            self.move_x_new.append(self.move_x_source[len(self.move_x_source)-1] + self.move_event[i].x_change)
            self.move_y_new.append(self.move_y_source[len(self.move_y_source)-1] + self.move_event[i].y_change)
        colour = ['b', 'r']
        plt.figure()
        for a in np.arange(0, 2):
            for b in np.arange(0, len(self.com[a].ft)):
                [x, y] = self.com[a].ft[b].getLocs()
                plt.scatter(x, y, marker='.', c=colour[a])
        for a in np.arange(0, len(self.move_x_source)):
            plt.plot([self.move_x_source[a], self.move_x_new[a]], [self.move_y_source[a], self.move_y_new[a]], c='k')
        plt.title('Move Events')
        plt.show()
        self.move_x_source = []
        self.move_y_source = []
        self.move_x_new = []
        self.move_y_new = []
    
    def plotFiring(self):
        for i in np.arange(0, len(self.fire_event)):
            source = self.fire_event[i].source
            target = self.fire_event[i].target
            self.fire_x_source.append(self.com[source[0]].ft[source[1]].man[source[2]].loc[0])
            self.fire_y_source.append(self.com[source[0]].ft[source[1]].man[source[2]].loc[1])
            self.fire_x_target.append(self.com[target[0]].ft[target[1]].man[target[2]].loc[0])
            self.fire_y_target.append(self.com[target[0]].ft[target[1]].man[target[2]].loc[1])
        colour = ['b', 'r']
        plt.figure()
        for a in np.arange(0, 2):
            for b in np.arange(0, len(self.com[a].ft)):
                [x, y] = self.com[a].ft[b].getLocs()
                plt.scatter(x, y, marker='.', c=colour[a])
        for a in np.arange(0, len(self.fire_x_source)):
            plt.plot([self.fire_x_source[a], self.fire_x_target[a]], [self.fire_y_source[a], self.fire_y_target[a]], c='k')
        plt.title('Fire Events')
        plt.show()
        self.fire_x_source = []
        self.fire_y_source = []
        self.fire_x_target = []
        self.fire_y_target = []
    
    def createMoveEvent(self, source, target):
        self.move_event.append(MoveEvent(source, target))
        
    def createFireEvent(self, source, target):
        self.fire_event.append(FireEvent(source, target))
    
    def updateScores(self):
        for i in np.arange(0, 2):
            self.score[i].append(self.com[i].countActive())
    
    def defineZones(self):
        zone_width = 100
        x_bound = [-1000, 1000]
        y_bound = [-1000, 1000]
        num = [(x_bound[1] - x_bound[0]) / zone_width, (y_bound[1] - y_bound[0]) / zone_width]
        x_ctr = np.linspace(-950, 950, num=num[0])
        y_ctr = np.linspace(-950, 950, num=num[1])
        self.zone = []
        for a in np.arange(0, len(x_ctr)):
            zone_row = []
            for b in np.arange(0, len(y_ctr)):
                zone_row.append(Zone(x_ctr[a], y_ctr[b], zone_width))
            self.zone.append(zone_row)
    
    def tick(self):
        self.t += 1
        # Commander assessment
        for i in np.arange(0, 2):
            self.com[i].assessBattle(self)
            self.com[i].assignOrders(self)
        # Order processing
        for i in np.arange(0, 2):
            for j in np.arange(0, len(self.com[i].ft)):
                self.com[i].ft[j].tick(self)
        # Event calculation
        for i in np.arange(0, len(self.move_event)):
            self.move_event[i].effect(self)
        for i in np.arange(0, len(self.fire_event)):
            self.fire_event[i].effect(self)
        # Reset exchanged_fire boolean
        for i in np.arange(0, 2):
            for j in np.arange(0, len(self.com[i].ft)):
                for k in np.arange(0, len(self.com[i].ft[j].man)):
                    self.com[i].ft[j].man[k].exchanged_fire = False
        # Affect results
        for i in np.arange(0, len(self.move_event)):
            self.move_event[i].apply(self)
        for i in np.arange(0, len(self.fire_event)):
            self.fire_event[i].apply(self)
        # Plot actions
        if np.mod(self.t, 10) == 0:
            print(self.t)
            self.plotMovements()
            self.plotFiring()
        # Store events
        self.move_event_record.append(self.move_event)
        self.fire_event_record.append(self.fire_event)
        # Clear events
        self.move_event = []
        self.fire_event = []
        self.updateScores()
    
    def collectLogs(self):
        move_event_record = self.move_event_record
        fire_event_record = self.fire_event_record
        order_record = []
        for i in np.arange(0, 2):
            order_record.append(self.com[i].order_record)
        return [move_event_record, fire_event_record, order_record]

class Commander(object):
    def __init__(self, id_num, unit_count, unit_loc, mission_objective):
        self.id_num = id_num
        self.enemy_id_num = np.where(np.arange(0, 2) != self.id_num)[0][0]
        self.score = 0
        self.ft = []
        for i in np.arange(0, unit_count):
            self.ft.append(Fireteam(unit_loc[i], self.id_num, self.enemy_id_num, i))
        self.mission_objective = mission_objective
        self.ini_strength = self.assessFriendlyStrength()
        self.order_record = []
        self.enemy_obj_infl_power = 1.0
        self.zone_importance = 1.0
        self.elim_enemy_ft_importance = 1.0
    
    def getLocs(self):
        x_loc = []
        y_loc = []
        for i in np.arange(0, len(self.ft)):
            x_loc.append(self.ft[i].loc[0])
            y_loc.append(self.ft[i].loc[1])
        return [x_loc, y_loc]
    
    def assessBattle(self, env):
        # Check force strengths
#        friendly_strength = self.assessFriendlyStrength()
#        enemy_strength = self.assessEnemyStrength(env)
        # Check influence over objective
        self.friendly_obj_influence = self.assessFriendlyObjInfl(env)
        self.enemy_obj_influence = np.asarray(self.assessEnemyObjInlf(env))
        # Generate task list:
        task = []
        # 1. Zone control
        for a in np.arange(0, len(env.zone)):
            for b in np.arange(0, len(env.zone[a])):
                x_mis_obj_ctr = np.mean(self.mission_objective[1][0])
                y_mis_obj_ctr = np.mean(self.mission_objective[1][1])
                x_dist = x_mis_obj_ctr - env.zone[a][b].x_ctr
                y_dist = y_mis_obj_ctr - env.zone[a][b].y_ctr
                dist = np.sqrt(x_dist**2 + y_dist**2)
                payoff = self.zone_importance * (1 / dist)
                cost = env.zone[a][b].menInZone(env)[self.enemy_id_num]
                task.append(Task('CONTROL ZONE', [a, b], payoff, cost))
        # 2. Enemy fireteam elimination
        for a in np.arange(0, len(env.com[self.enemy_id_num].ft)):
            payoff = self.elim_enemy_ft_importance
            cost = env.com[self.enemy_id_num].ft[a].countActive()
            task.append(Task('ELIM FT', a, payoff, cost))
        
    def assessFriendlyStrength(self):
        man_value = 1
        man_active = 0
        for i in np.arange(0, len(self.ft)):
            man_active += self.ft[i].countActive()
        man_strength = man_active * man_value
        return man_strength
    
    def assessEnemyStrength(self, env):
        return env.com[self.enemy_id_num].assessFriendlyStrength()
    
    def assessFriendlyObjInfl(self, env):
        infl = []
        for i in np.arange(0, len(self.ft)):
            # Proximity to mission objective
            x_dist = np.min([np.absolute(self.ft[i].loc[0] - self.mission_objective[1][0][0]), np.absolute(self.ft[i].loc[0] - self.mission_objective[1][0][1])])
            y_dist = np.min([np.absolute(self.ft[i].loc[1] - self.mission_objective[1][1][0]), np.absolute(self.ft[i].loc[1] - self.mission_objective[1][1][1])])
            obj_dist = np.sqrt(x_dist**2 + y_dist**2)
            # Number of active men in fireteam
            active = self.ft[i].countActive()
            # Calculate influence
            infl.append((1 / obj_dist) * active)
        return infl
    
    def assessEnemyObjInlf(self, env):
        return env.com[self.enemy_id_num].assessFriendlyObjInfl(env)
    
    def assessEnemyUnitInfl(self, env):
        return env.com[self.enemy_id_num].assessFriendlyUnitInfl()
    
    def assignOrders(self, env):
        for i in np.arange(0, len(self.ft)):
            # Always assign an attack order
            action = 1
            # Weight potential targets by objective influence raised to a power
            infl_raised = self.enemy_obj_influence ** self.enemy_obj_infl_power
            total_weight = np.sum(infl_raised)
            rel_weight = infl_raised / total_weight
            cum_weight = []
            for a in np.arange(0, len(rel_weight)):
                cum_weight.append(np.nansum(rel_weight[0:a+1]))
            if cum_weight[-1] == 0:
                # No enemy fireteam has influence over objective, give no order
                action = 0
                target = []
            else:
                rand_select = np.random.uniform()
                found_select = False
                a = 0
                while found_select == False:
                    if rand_select < cum_weight[a]:
                        found_select = True
                    else:
                        a += 1
                target = [env.com[self.enemy_id_num].ft[a].loc[0], env.com[self.enemy_id_num].ft[a].loc[1]]
            order = Order(env.t, action, target)
            self.ft[i].order = order
            self.order_record.append(order)
    
    def countActive(self):
        active = 0
        for i in np.arange(0, len(self.ft)):
            active += self.ft[i].countActive()
        return active
    
#    def genRandomOrder(self, env):
#        action = np.random.randint(0, 4)
#        if action == 0:
#            order = Order(env.t, action)
#        elif action == 1:
#            if np.random.uniform() < 0.5:
#                target = [0, 0]
#            else:
#                enemy_locs = env.com[self.enemy_id_num].getLocs()
#                enemy_target = np.random.randint(0, len(enemy_locs[0]))
#                target = [enemy_locs[0][enemy_target], enemy_locs[1][enemy_target]]
#            order = Order(env.t, action, target)
#        elif action == 2:
#            order = Order(env.t, action)
#        elif action == 3:
#            target = [-100]
#            order = Order(env.t, action, target)
#        return order

class Fireteam(object):
    def __init__(self, loc, com_id_num, com_enemy_id_num, ft_id_num):
        # Create soldier instances
        self.man = []
        for i in np.arange(0, 4):
            self.man.append(Man(loc, com_id_num, com_enemy_id_num))
        [x, y] = self.getLocs()
        self.loc = [np.mean(x), np.mean(y)]
        self.id_num = ft_id_num
        self.com_id_num = com_id_num
        self.com_enemy_id_num = com_enemy_id_num
        self.order = Order(0, 0)
        self.speed = 5
            
    def getLocs(self):
        x_loc = []
        y_loc = []
        for i in np.arange(0, len(self.man)):
            if self.man[i].stance != 'DEAD':
                x_loc.append(self.man[i].loc[0])
                y_loc.append(self.man[i].loc[1])
        return [x_loc, y_loc]
    
    def countActive(self):
        active = 0
        for i in np.arange(0, len(self.man)):
            if self.man[i].active == True:
                active += 1
        return active
    
    def tick(self, env):
        [x, y] = self.getLocs()
        self.loc = [np.mean(x), np.mean(y)]
        if self.order.action == 1:
            for i in np.arange(0, len(self.man)):
                env.createMoveEvent([self.com_id_num, self.id_num, i], self.order.target)
        # Check if engaged
        for i in np.arange(0, len(self.man)):
            if self.man[i].exchanged_fire == False:
                if self.man[i].stance == 'ENGAGED':
                    self.man[i].stance = 'FREE'
            else:
                self.man[i].stance = 'ENGAGED'
        # Get potential targets
        in_range = []
        for i in np.arange(0, len(self.man)):
            if self.man[i].stance != 'DEAD':
                in_range.append(self.man[i].identify_targets(env))
        # Direct fire
        for i in np.arange(0, len(self.man)):
            if self.man[i].stance != 'DEAD':
                if self.man[i].active == True:
                    if len(self.man[i].in_range) > 0:
                        target = np.random.randint(0, len(self.man[i].in_range))
                        self.man[i].fire_target = self.man[i].in_range[target]
                        env.createFireEvent([self.com_id_num, self.id_num, i], [self.com_enemy_id_num, self.man[i].fire_target[0], self.man[i].fire_target[1]])

class Man(object):
    def __init__(self, loc, id_num, enemy_id_num):
        self.id_num = id_num
        self.enemy_id_num = enemy_id_num
        self.loc = loc
        self.effective_range = 500
        self.speed = 1.83
        self.active = True
        self.stance = 'FREE'
        self.exchanged_fire = False
        
    def assessInfluence(self):
        return [self.loc[0], self.loc[1], self.effective_range]
    
    def identify_targets(self, env):
        # Check for enemy within effective range
        in_range = []
        if self.stance != 'DEAD':
            for i in np.arange(0, len(env.com[self.enemy_id_num].ft)):
                for j in np.arange(0, len(env.com[self.enemy_id_num].ft[i].man)):
                    if env.com[self.enemy_id_num].ft[i].man[j].stance != 'DEAD':
                        if env.com[self.enemy_id_num].ft[i].man[j].active == True:
                            # SOME SOLDIERS SEEM TO BE MARKED DEAD BUT STILL ACTIVE
                            x_dist = env.com[self.enemy_id_num].ft[i].man[j].loc[0] - self.loc[0]
                            y_dist = env.com[self.enemy_id_num].ft[i].man[j].loc[1] - self.loc[1]
                            dist = np.sqrt(x_dist**2 + y_dist**2)
                            if dist < self.effective_range:
                                in_range.append([i, j])
        self.in_range = in_range
        return in_range

class Order(object):
    """ 
    Action:       Priority:
    0 : NONE      0 : Regular
    1 : ATTACK    1 : High
    2 : DEFEND
    3 : RETREAT
    """
    def __init__(self, t, action, target=[], priority=0):
        self.t = t
        self.action = action
        self.target = target

class MoveEvent(object):
    def __init__(self, source, target):
        self.source = source # Commander, fireteam, and soldier indexes for source
        self.target = target # [x, y] coordinates for destination
    
    def effect(self, env):
        if env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].stance != 'DEAD':
            if env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].active == True:
                if env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].stance != 'ENGAGED':
                    x_dist = self.target[0] - env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[0]
                    y_dist = self.target[1] - env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[1]
                    dist = np.sqrt(x_dist**2 + y_dist**2)
                    speed = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].speed
                    x_change = (speed / dist) * x_dist
                    y_change = (speed / dist) * y_dist
                else:
                    x_change = 0
                    y_change = 0
            else:
                x_change = 0
                y_change = 0
        else:
            x_change = 0
            y_change = 0
        self.x_change = x_change # Change in x coordinate for movement in this timestep
        self.y_change = y_change # Change in y coordinate for movement in this timestep
    
    def apply(self, env):
        self.t = env.t
        self.ini_loc = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc
        # Update soldier's position
        env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[0] += self.x_change
        env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[1] += self.y_change
        self.new_loc = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc
        
class FireEvent(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target
        
    def effect(self, env):
        x_dist = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[0] - env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[0]
        y_dist = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[1] - env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc[1]
        dist = np.sqrt(x_dist**2 + y_dist**2)
        effective_range = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].effective_range
        if np.random.uniform() < hitProb(dist, effective_range):
            self.result = 'HIT'
        else:
            self.result = 'MISS'
        
    def apply(self, env):
        self.t = env.t
        self.source_loc = env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].loc
        self.target_loc = env.com[self.target[0]].ft[self.target[1]].man[self.target[2]].loc
        env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].stance = 'ENGAGED'
        env.com[self.source[0]].ft[self.source[1]].man[self.source[2]].exchanged_fire = True
        env.com[self.target[0]].ft[self.target[1]].man[self.target[2]].stance = 'ENGAGED'
        env.com[self.target[0]].ft[self.target[1]].man[self.target[2]].exchanged_fire = True
        if self.result == 'HIT':
            env.com[self.target[0]].ft[self.target[1]].man[self.target[2]].stance = 'DEAD'
            env.com[self.target[0]].ft[self.target[1]].man[self.target[2]].active = False

class Zone(object):
    def __init__(self, x_ctr, y_ctr, width):
        self.x_ctr = x_ctr
        self.y_ctr = y_ctr
        self.width = width
    
    def menInZone(self, env):
        men = [0, 0]
        for i in np.arange(0, len(env.com)):
            for j in np.arange(0, len(env.com[i].ft)):
                ft_loc = env.com[i].ft[j].loc
                if ft_loc[0] >= self.x_ctr - (self.width / 2):
                    if ft_loc[0] < self.x_ctr + (self.width / 2):
                        if ft_loc[1] >= self.y_ctr - (self.width / 2):
                            if ft_loc[1] < self.y_ctr + (self.width / 2):
                                men[i] += env.com[i].ft[j].countActive()
        return men

class Task(object):
    def __init__(self, task_type, target, payoff, cost):
        self.type = task_type
        self.target = target
        self.payoff = payoff
        self.cost = cost
        self.value = payoff / cost

def hitProb(dist, effective_range):
    c = 0.11875
    m = - 0.1125 / effective_range
    hit_prob = (m * dist) + c
    return hit_prob

def outputLogs(env):
    [move_event_record, fire_event_record, order_record] = env.collectLogs()
    # Save move events
    move_log = []
    for i in np.arange(0, len(move_event_record)):
        for j in np.arange(0, len(move_event_record[i])):
            event_j_in_timestep_i = move_event_record[i][j]
            t = event_j_in_timestep_i.t
            commander_id = event_j_in_timestep_i.source[0]
            fireteam_id = event_j_in_timestep_i.source[1]
            soldier_id = event_j_in_timestep_i.source[2]
            destination_x = event_j_in_timestep_i.target[0]
            destination_y = event_j_in_timestep_i.target[1]
            ini_x = event_j_in_timestep_i.ini_loc[0]
            ini_y = event_j_in_timestep_i.ini_loc[1]
            x_change = event_j_in_timestep_i.x_change
            y_change = event_j_in_timestep_i.y_change
            new_x = event_j_in_timestep_i.new_loc[0]
            new_y = event_j_in_timestep_i.new_loc[1]
            output_row = [t, commander_id, fireteam_id, soldier_id, destination_x, destination_y, ini_x, ini_y, x_change, y_change, new_x, new_y]
            move_log.append(output_row)
    # Save fire events
    fire_log = []
    for i in np.arange(0, len(fire_event_record)):
        for j in np.arange(0, len(fire_event_record[i])):
            event_j_in_timestep_i = fire_event_record[i][j]
            t = event_j_in_timestep_i.t
            source_commander_id = event_j_in_timestep_i.source[0]
            source_fireteam_id = event_j_in_timestep_i.source[1]
            source_soldier_id = event_j_in_timestep_i.source[2]
            target_commander_id = event_j_in_timestep_i.target[0]
            target_fireteam_id = event_j_in_timestep_i.target[1]
            target_soldier_id = event_j_in_timestep_i.target[2]
            source_x = event_j_in_timestep_i.source_loc[0]
            source_y = event_j_in_timestep_i.source_loc[1]
            target_x = event_j_in_timestep_i.target_loc[0]
            target_y = event_j_in_timestep_i.target_loc[1]
            result = event_j_in_timestep_i.result
            output_row = [t, source_commander_id, source_fireteam_id, source_soldier_id, target_commander_id, target_fireteam_id, target_soldier_id, source_x, source_y, target_x, target_y, result]
            fire_log.append(output_row)
    with open('fire_log.txt', 'w') as output_file:
        wr = csv.writer(output_file)
        for a in fire_log:
            wr.writerow(a)
    # Save orders
    order_log = []
    for i in np.arange(0, len(order_record)):
        for j in np.arange(0, len(order_record[i])):
            commander_i_order_j = order_record[i][j]
            t = commander_i_order_j.t
            action = commander_i_order_j.action
            target = commander_i_order_j.target
            output_row = [t, action, target]
            order_log.append(output_row)
    with open('order_log.txt', 'w') as output_file:
        wr = csv.writer(output_file)
        for a in order_log:
            wr.writerow(a)

def fireActivity():
    with open('fire_log.txt', 'r') as input_file:
        r = csv.reader(input_file, delimiter=',')
        source_x = []
        source_y = []
        target_x = []
        target_y = []
        for row in r:
            if row:
                source_x.append(float(row[7]))
                source_y.append(float(row[8]))
                target_x.append(float(row[9]))
                target_y.append(float(row[10]))
    # Plot fire source locations
    plt.figure()
    plt.scatter(source_x, source_y, marker='x')
    plt.title('Fire Source Locations')
    plt.show()
    # Plot fire target locations
    plt.figure()
    plt.scatter(target_x, target_y, marker='x')
    plt.title('Fire Target Locations')
    plt.show()
    all_x = np.asarray(source_x + target_x)
    all_y = np.asarray(source_y + target_y)
    x_grid = np.arange(np.floor(np.min(all_x))-10, np.ceil(np.max(all_x))+10, 10)
    y_grid = np.arange(np.floor(np.min(all_y))-10, np.ceil(np.max(all_y))+10, 10)
    xx = []
    yy = []
    zz = []
    for a in np.arange(0, len(x_grid)-1):
        lo_x = x_grid[a]
        hi_x = x_grid[a+1]
        x = []
        y = []
        z = []
        for b in np.arange(0, len(y_grid)-1):
            lo_y = y_grid[b]
            hi_y = y_grid[b+1]
            valid_x_I = np.where(np.logical_and(all_x >= lo_x, all_x < hi_x))
            valid_y_I = np.where(np.logical_and(all_y >= lo_y, all_y < hi_y))
            all_I = np.unique(np.append(valid_x_I, valid_y_I))
            valid_I = []
            for i in all_I:
                if np.any(valid_x_I == i):
                    if np.any(valid_y_I == i):
                        valid_I.append(i)
            grid_count = len(valid_I)
            x.append((x_grid[a] + x_grid[a+1]) / 2)
            y.append((y_grid[b] + y_grid[b+1]) / 2)
            z.append(grid_count)
        xx.append(x)
        yy.append(y)
        zz.append(z)
    # Plot fire intensity
    plt.figure()
    plt.contourf(xx, yy, zz)
    plt.title('Fire Intensity')
    plt.show()

def friendlyCasualties(id_num):
    with open('fire_log.txt', 'r') as input_file:
        r = csv.reader(input_file, delimiter=',')
        target_x = []
        target_y = []
        for row in r:
            if row:
                commander_id = int(row[4])
                if commander_id == id_num:
                    result = row[11]
                    if result == 'HIT':
                        target_x.append(float(row[9]))
                        target_y.append(float(row[10]))
    # Plot casualty locations
    plt.figure()
    plt.scatter(target_x, target_y, marker='x')
    plt.title('Friendly Casualty Locations')
    plt.show()
    x_grid = np.arange(np.floor(np.min(target_x))-10, np.ceil(np.max(target_x))+10, 10)
    y_grid = np.arange(np.floor(np.min(target_y))-10, np.ceil(np.max(target_y))+10, 10)
    xx = []
    yy = []
    zz = []
    for a in np.arange(0, len(x_grid)-1):
        lo_x = x_grid[a]
        hi_x = x_grid[a+1]
        x = []
        y = []
        z = []
        for b in np.arange(0, len(y_grid)-1):
            lo_y = y_grid[b]
            hi_y = y_grid[b+1]
            valid_x_I = np.where(np.logical_and(target_x >= lo_x, target_x < hi_x))
            valid_y_I = np.where(np.logical_and(target_y >= lo_y, target_y < hi_y))
            all_I = np.unique(np.append(valid_x_I, valid_y_I))
            valid_I = []
            for i in all_I:
                if np.any(valid_x_I == i):
                    if np.any(valid_y_I == i):
                        valid_I.append(i)
            grid_count = len(valid_I)
            x.append((x_grid[a] + x_grid[a+1]) / 2)
            y.append((y_grid[b] + y_grid[b+1]) / 2)
            z.append(grid_count)
        xx.append(x)
        yy.append(y)
        zz.append(z)
    # Plot friendly casualty intensity
    plt.figure()
    plt.contourf(xx, yy, zz)
    plt.title('Friendly Casualty Intensity')
    plt.show()
    
# Initialise simulation
env = Environment()

# Plot scenario start
env.plotLocations()

# Step through simulation
for t in np.arange(0, 150):
    env.tick()

# Plot commanders' score over time
env.plotScore()

# Output final scores
print('Commander 0:')
print(env.score[0][-1])
print('Commander 1:')
print(env.score[1][-1])

# Collect event and order logs
outputLogs(env)

# Perform post analysis
fireActivity()
friendlyCasualties(0)