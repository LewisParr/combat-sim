# -*- coding: utf-8 -*-
# order.py

class Order(object):
    """
    Order is base class providing an interface for all subsequent (inherited)
    orders.
    """
    pass

class MoveTo(Order):
    """
    MoveTo order is given to relocate a unit when it is not expected to 
    encounter opposition.
    """
    def __init__(self, target):
        """
        target - (x, y) location
        """
        self.type = 'MOVETO'
        self.target = target

class Hold(Order):
    """
    Hold order is given to have a unit hold its current position.
    """
    def __init__(self):
        self.type = 'HOLD'

class Defend(Order):
    """
    Defend order is given to have a unit fortify and defend its position.
    """
    def __init__(self):
        self.type = 'DEFEND'