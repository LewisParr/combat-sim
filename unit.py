# -*- coding: utf-8 -*-
# unit.py

import infantryasset
import armourasset
import artilleryasset

import numpy as np

class Unit(object):
    """
    Unit is base class providing an interface for all subsequent 
    (inherited) units.
    """
    pass

class fHeadquarters(Unit):
    """
    fHeadquarters is a general class for the family of headquarters units.
    """
    def __init__(self):
        self.familyID = 1
        
class Headquarters(fHeadquarters):
    """
    ...
    """
    def __init__(self):
        self.unitID = 1

class fInfantry(Unit):
    """
    fInfantry is a general class for the family of infantry units.
    """
    def __init__(self):
        self.familyID = 2

class Infantry(fInfantry):
    """
    ...
    """
    def __init__(self, nRifleman=4, nAutomaticRifleman=2, nMarksman=2):
        self.unitID = 2
        # Initialise assets
        self.member = []
        manID = 0
        for R in np.arange(0, nRifleman):
            self.member.append(infantryasset.Rifleman(manID))
            manID += 1
        for A in np.arange(0, nAutomaticRifleman):
            self.member.append(infantryasset.AutomaticRifleman(manID))
            manID += 1
        for M in np.arange(0, nMarksman):
            self.member.append(infantryasset.Marksman(manID))
            manID += 1
    
    def setLocation(self, location):
        [x, y] = location
        for M in self.member:
            M.setLocation([x + np.random.random(), y + np.random.random()])
    
    def setOrder(self, order):
        self.order = order
    
    def detect(self, env, enemy_force):
        # Attempt to detect any visible enemy assets
        detected_location = []
        for M in self.member:
            detected_location.append(M.detect(env, enemy_force))
        return detected_location
    
    def createEvents(self, env, enemy_force):
        # Decide on actions to complete order
        if self.order.type == 'MOVETO':
            [manID, eventType, eventData] = self.moveTo(self.order.target)
        return [manID, eventType, eventData]
    
    def moveTo(self, target):
        all_manID = []
        all_eventType = []
        all_eventData = []
        for M in self.member:
            [manID, change] = M.moveTo(target)
            all_manID.append(manID)
            all_eventType.append('MOVE')
            all_eventData.append(change)
        return [all_manID, all_eventType, all_eventData]

class AmphibiousInfantry(fInfantry):
    """
    ...
    """
    def __init__(self):
        self.unitID = 3

class MechanisedInfantry(fInfantry):
    """
    ...
    """
    def __init__(self):
        self.unitID = 4
        
class MotorisedInfantry(fInfantry):
    """
    ...
    """
    def __init__(self):
        self.unitID = 5

class InfantryHeavyWeapons(fInfantry):
    """
    ...
    """
    def __init__(self):
        self.unitID = 6
        
class Sniper(fInfantry):
    """
    ...
    """
    def __init__(self):
        self.unitID = 7

class fArmCavRec(Unit):
    """
    fArmCavRec is a general class for the family of armour, cavalry and 
    reconnaissance units.
    """
    def __init__(self):
        self.familyID = 3

class Armour(fArmCavRec):
    """
    ...
    """
    def __init__(self):
        self.unitID = 8

class Reconnaissance(fArmCavRec):
    """
    ...
    """
    def __init__(self):
        self.unitID = 9

class ArmouredReconnaissance(fArmCavRec):
    """
    ...
    """
    def __init__(self):
        self.unitID = 10

class fArtillery(Unit):
    """
    fArtillery is a general class for the family of artillery units.
    """
    def __init__(self):
        self.familyID = 4

class Artillery(fArtillery):
    """
    ...
    """
    def __init__(self):
        self.unitID = 11

class Mortars(fArtillery):
    """
    ...
    """
    def __init__(self):
        self.unitID = 12

class ArtilleryObservation(fArtillery):
    """
    ...
    """
    def __init__(self):
        self.unitID = 13

class fEngineer(Unit):
    """
    fEngineer is a general class for the family of engineer units.
    """
    def __init__(self):
        self.familyID = 5

class Engineer(fEngineer):
    """
    ...
    """
    def __init__(self):
        self.unitID = 14

class Bridging(fEngineer):
    """
    ...
    """
    def __init__(self):
        self.unitID = 15

class EngExpOrdDis(fEngineer):
    """
    Engineer Explosive Ordinance Disposal.
    """
    def __init__(self):
        self.unitID = 16

class fAirDefenceAntiTank(Unit):
    """
    fAirDefenceAntiTank is a general class for the family of air defence
    and anti-tank units.
    """
    def __init__(self):
        self.familyID = 6

class AirDefence(fAirDefenceAntiTank):
    """
    ...
    """
    def __init__(self):
        self.unitID = 17

class AntiTank(fAirDefenceAntiTank):
    """
    ...
    """
    def __init__(self):
        self.unitID = 18

class fAviation(Unit):
    """
    fAviation is a general class for the family of aviation units.
    """
    def __init__(self):
        self.familyID = 7

class Aviation(fAviation):
    """
    ...
    """
    def __init__(self):
        self.unitID = 19

class fSpecialOperationsForce(Unit):
    """
    fSpecialOperationsForce is a general class for the family of special 
    operations units.
    """
    def __init__(self):
        self.familyID = 8

class SAS(fSpecialOperationsForce):
    """
    ...
    """
    def __init__(self):
        self.unitID = 20
        
class Marines(fSpecialOperationsForce):
    """
    ...
    """
    def __init__(self):
        self.unitID = 21