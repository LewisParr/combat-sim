# -*- coding: utf-8 -*-
# infantryasset.py

class InfantryAsset(object):
    """
    InfantryAsset is base class providing an interface for all subsequent 
    (inherited) infantry assets.
    """
    pass

class Rifleman(InfantryAsset):
    """
    Rifleman represents an infantryman equipped primarily with small arms
    rifle variants.
    """
    pass

class AutomaticRifleman(InfantryAsset):
    """
    AutomaticRifleman represents an infantryman equipped primarily with small
    arms light machine gun or light support weapon variants.
    """
    pass

class Marksman(InfantryAsset):
    """
    Marksman represents an infantryman equipped primarily with small arms
    marksman rifle variants.
    """
    pass