# -*- coding: utf-8 -*-
# headquartersasset.py

class HeadquartersAsset(object):
    """
    Headquarters is base class providing an interface for all subsequent 
    (inherited) headquarters assets.
    """
    pass

class FOB(HeadquartersAsset):
    def setLocation(self, location):
        self.location = location