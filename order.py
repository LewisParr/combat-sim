# -*- coding: utf-8 -*-
# order.py

class Order(object):
    """
    Order is base class providing an interface for all subsequent (inherited)
    orders.
    """
    pass

class MoveTo(object):
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