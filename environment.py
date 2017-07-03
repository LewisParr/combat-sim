# -*- coding: utf-8 -*-
# environment.py

import numpy as np

class Environment(object):
    """
    ...
    """
    def genTerrain(self, nX, nY, F):
        x = np.arange(0, nX)
        y = np.arange(0, nY)
        xx, yy = np.meshgrid(x, y)
        i = []
        j = []
        for a in x:
            i_row = []
            j_row = []
            for b in y:
                i_row.append(np.min([xx[a][b], nX-xx[a][b]]))
                j_row.append(np.min([yy[a][b], nY-yy[a][b]]))
                #j_row.append()
            i.append(i_row)
            j.append(j_row)
        H = np.exp(-0.5 * (np.square(i) + np.square(j)) / F**2)
        Z = np.real(np.fft.ifft2(H * np.fft.ifft2(np.random.normal(0, 1, [nX, nY]))))
        self.nX = nX
        self.nY = nY
        self.X = xx
        self.Y = yy
        self.Z = Z
    
    pass

class EnvironmentObject(object):
    """
    EnvironmentObject is a base class providing an interface for all 
    subsequent (inherited) environment objects.
    """
    pass