# -*- coding: utf-8 -*-
# environment.py

import csv
import numpy as np
import matplotlib.pyplot as plt

class Environment(object):
    """
    ...
    """
    def __init__(self, nX, nY):
        self.nX = nX
        self.nY = nY
        # Create terrain cells
        self.terrain_cell = []
        for x in np.arange(0, self.nX):
            terrain_cell_row = []
            for y in np.arange(0, self.nY):
                terrain_cell_row.append(TerrainCell())
            self.terrain_cell.append(terrain_cell_row)
        # Create visibility cells
        self.visibility_cell_width = 20 # Terrain cells per visibility cell
        self.visibility_cell = []
        for x in np.arange(0, self.nX / self.visibility_cell_width):
            visibility_cell_row = []
            x_ctr = (self.visibility_cell_width / 2) + (x * self.visibility_cell_width)
            for y in np.arange(0, self.nY / self.visibility_cell_width):
                y_ctr = (self.visibility_cell_width / 2) + (y * self.visibility_cell_width)
                visibility_cell_row.append(VisibilityCell(x_ctr, y_ctr))
            self.visibility_cell.append(visibility_cell_row)
        
    def genTerrain(self, F):
        """
        ...
        """
        x = np.arange(0, self.nX)
        y = np.arange(0, self.nY)
        xx, yy = np.meshgrid(x, y)
        i = []
        j = []
        for a in x:
            i_row = []
            j_row = []
            for b in y:
                i_row.append(np.min([xx[a][b], self.nX-xx[a][b]]))
                j_row.append(np.min([yy[a][b], self.nY-yy[a][b]]))
            i.append(i_row)
            j.append(j_row)
        H = np.exp(-0.5 * (np.square(i) + np.square(j)) / F**2)
        Z = np.real(np.fft.ifft2(H * np.fft.ifft2(np.random.normal(0, 1, [self.nX, self.nY]))))
        # Save Z values to respective terrain cells
        for x in np.arange(0, self.nX):
            for y in np.arange(0, self.nY):
                self.terrain_cell[x][y].setElevation(Z[x][y])
    
    def getTerrainCellElevations(self):
        Z = []
        for x in np.arange(0, self.nX):
            Z_row = []
            for y in np.arange(0, self.nY):
                Z_row.append(self.terrain_cell[x][y].Z)
            Z.append(Z_row)
        return Z
    
    def plotElevation(self):
        X, Y = np.meshgrid(np.arange(0, self.nX), np.arange(0, self.nY))
        Z = self.getTerrainCellElevations()
        plt.figure()
        plt.contourf(X, Y, Z)
        plt.title('Elevation Contour Plot')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Terrain Elevation')
        plt.colorbar()
        plt.show()

    def saveElevationData(self):
        with open('elevation.txt', 'w') as output_file:
            wr = csv.writer(output_file)
            for x in np.arange(0, self.nX):
                for y in np.arange(0, self.nY):
                    z = self.terrain_cell[x][y].Z
                    #z = self.Z[a][b] OLD
                    output = [x, y, z]
                    wr.writerow(output)
                    
    def loadElevationData(self):
        with open('elevation.txt', 'r') as input_file:
            r = csv.reader(input_file)
            for row in r:
                if row:
                    x = int(row[0])
                    y = int(row[1])
                    z = float(row[2])
                    self.terrain_cell[x][y].setElevation(z)
            x = np.arange(0, self.nX)
            y = np.arange(0, self.nY)
            self.X, self.Y = np.meshgrid(x, y)
            
    def buildVisibilityMaps(self):
        for x in np.arange(0, self.nX / self.visibility_cell_width):
            print(x)
            for y in np.arange(0, self.nY / self.visibility_cell_width):
                print(y)
                observer = [self.visibility_cell[int(x)][int(y)].x_ctr, self.visibility_cell[int(x)][int(y)].y_ctr]
                [xx, yy, v_map] = self.buildVisibilityMap(observer)
                self.visibility_cell[int(x)][int(y)].setMap(v_map)
    
    def buildVisibilityMap(self, obs):
        bearing = np.linspace(0, 179, 90)
        all_x = []
        all_y = []
        all_v = []
        for b in bearing:
            if b == 0:
                # Undefined slope
                pass
            elif b == 90:
                # Zero issues
                pass
            else:
                # Convert observer position and bearing to y = mx + c linear equation
                r = (b / 360) * 2 * np.pi
                if r < np.pi / 2:
                    m = np.tan((np.pi / 2) - r)
                elif r < np.pi:
                    m = - np.tan(r - (np.pi / 2))
                elif r < (3 / 2) * np.pi:
                    m = np.tan(((3 / 2) * np.pi) - r)
                else:
                    m = - np.tan(r - ((3 / 2) * np.pi))
                c = obs[1] - (m * obs[0])
#                # Plot the slice line
#                plt.figure()
#                plt.contourf(self.X, self.Y, self.Z)
#                x = []
#                y = []
#                for a in np.linspace(0, self.nX):
#                    if (m * a) + c >= 0:
#                        if (m * a) + c < self.nY:
#                            x.append(a)
#                            y.append((m * a) + c)
#                plt.plot(x, y, c='r')
#                plt.show()
                [slice_x, slice_y, slice_v] = self.calculateSliceVisibility(obs, m, c)
                all_x = all_x + slice_x
                all_y = all_y + slice_y
                all_v = all_v + slice_v
        # Plot all visible points
        all_x = np.asarray(all_x)
        all_y = np.asarray(all_y)
        all_v = np.asarray(all_v)
#        I = np.where(all_v)
#        plt.figure()
#        plt.contourf(self.X, self.Y, self.Z)
#        plt.scatter(all_x[I], all_y[I], c='g') # SEEMS TO BE MIRRORED ALONG y = x
#        plt.show()
        # Estimate probability of each point being visible
        grid_width = self.visibility_cell_width
        x = [grid_width/2]
        while x[-1] + grid_width/2 < self.nX-1:
            x.append(x[-1] + grid_width)
        y = [grid_width/2]
        while y[-1] + grid_width/2 < self.nY-1:
            y.append(y[-1] + grid_width)
        v_prob = []
        for a in np.arange(0, len(x)-1):
            row_v_prob = []
            for b in np.arange(0, len(y)-1):
                lo_x = x[a]
                hi_x = x[a+1]
                lo_y = y[b]
                hi_y = y[b+1]
                over_lo_x = all_x >= lo_x
                under_hi_x = all_x < hi_x
                satisfy_x = np.logical_and(over_lo_x, under_hi_x)
                over_lo_y = all_y >= lo_y
                under_hi_y = all_y < hi_y
                satisfy_y = np.logical_and(over_lo_y, under_hi_y)
                in_grid = np.logical_and(satisfy_x, satisfy_y)
                grid_v = all_v[in_grid]
                g = 0
                b = 0
                for c in grid_v:
                    if c == True:
                        g += 1
                    else:
                        b += 1
                if (g + b) > 0:
                    grid_v_prob = g / (g + b)
                else:
                    grid_v_prob = 0
                row_v_prob.append(grid_v_prob)
            v_prob.append(row_v_prob)
        xx, yy = np.meshgrid(x[0:-1], y[0:-1])
        plt.figure()
        plt.contourf(xx, yy, v_prob)
        plt.show()
        return [xx, yy, v_prob]
            
    def calculateSliceVisibility(self, obs, m, c):
        # Define distance origin where line cuts axes
        if c > 0:
            los_x_o = 0
            los_y_o = c
        else:
            los_x_o = (-c / m)
            los_y_o = 0
        # Find elevation at x and y intercepts
        dist = np.empty(0)
        elev = np.empty(0)
        est_x_dist = np.empty(0)
        est_x_elev = np.empty(0)
        est_y_dist = np.empty(0)
        est_y_elev = np.empty(0)
        for a in np.arange(0, self.nX):
            a = int(a)
            if (m * a) + c >= 0:
                if (m * a) + c <= self.nY - 1:
                    if np.floor((m * a) + c) == ((m * a) + c):
                        # Point lies on slice line
                        b = int((m * a) + c)
                        dist = np.append(dist, np.array(np.sqrt((a - los_x_o)**2 + ((m * a) + c - los_y_o)**2)))
                        elev = np.append(elev, np.array(self.terrain_cell[a][b].Z))
                    else:
                        # Interpolation needed to estimate elevation at point
                        lo_b = int(np.floor((m * a) + c))
                        hi_b = int(np.ceil((m * a) + c))
                        beta = ((m * a) + c - lo_b) / (hi_b - lo_b)
                        lo_Z = self.terrain_cell[a][lo_b].Z
                        hi_Z = self.terrain_cell[a][hi_b].Z
                        est_x_dist = np.append(est_x_dist, np.array(np.sqrt((a - los_x_o)**2 + ((m * a) + c - los_y_o)**2)))
                        est_x_elev = np.append(est_x_elev, np.array(lo_Z * (1 - beta) + hi_Z * beta))
        for b in np.arange(0, self.nY):
            b = int(b)
            if (b - c) / m >= 0:
                if (b - c) / m <= self.nX - 1:
                    if np.floor((b - c) / m) != (b - c) / m:
                        # Interpolation needed to estimate elevation at point
                        lo_a = int(np.floor((b - c) / m))
                        hi_a = int(np.ceil((b - c) / m))
                        alpha = ((b - c) / m - lo_a) / (hi_a - lo_a)
                        lo_Z = self.terrain_cell[lo_a][b].Z
                        hi_Z = self.terrain_cell[hi_a][b].Z
                        est_y_dist = np.append(est_y_dist, np.array(np.sqrt((((b - c) / m) - los_x_o)**2 + (b - los_y_o)**2)))
                        est_y_elev = np.append(est_y_elev, np.array(lo_Z * (1 - alpha) + hi_Z * alpha))
        # Smooth estimated samples to better fit known values?
        # Combine sample vectors
        all_dist = np.append(dist, est_x_dist)
        all_dist = np.append(all_dist, est_y_dist)
        all_elev = np.append(elev, est_x_elev)
        all_elev = np.append(all_elev, est_y_elev)
        # Sort combined vectors for ascending distance from line origin
        dist = []
        elev = []
        dist = all_dist[all_dist.argsort()]
        elev = all_elev[all_dist.argsort()]
        # Find observer's position on line
        obs_dist = np.sqrt((obs[0] - los_x_o)**2 + ((m * obs[0]) + c - los_y_o)**2)
        j = np.where(dist == obs_dist)[0]
        if j.size > 0:
            j = j[0]
            # Scan the slice for line-of-sight
            los = []
            for i in np.arange(0, len(dist)):
                if i == j:
                    los.append(True)
                else:
                    los_c = ((dist[i] * elev[j]) - (dist[j] * elev[i])) / (dist[i] - dist[j])
                    los_m = (elev[i] - elev[j]) / (dist[i] - dist[j])
                    los_check = True
                    for k in np.arange(np.min([i, j]), np.max([i, j]), 1):
                        if elev[k] >= (los_m * dist[k]) + los_c:
                            los_check = False
                    los.append(los_check)
            # Plot point visibility along slice
    #        plt.figure()
    #        plt.plot(dist, elev)
    #        plt.scatter(dist[np.where(los)], elev[np.where(los)], c='g')
    #        plt.show()
            # Convert distance values back to (x, y) values
            x = []
            y = []
            v = []
            for i in np.arange(0, len(dist)):
                quada = 1 + m**2
                quadb = (2 * c * m) - (2 * los_x_o) - (2 * los_y_o * m)
                quadc = (los_x_o ** 2) + (c ** 2) - (2 * los_y_o * c) + (los_y_o ** 2) - (dist[i] ** 2)
                xx = (- quadb + np.sqrt((quadb ** 2) - (4 * quada * quadc))) / (2 * quada)
                yy = (m * xx) + c
                x.append(xx)
                y.append(yy)
                v.append(los[i])
            return [x, y, v]
        else:
            return [[], [], []]
    
    def saveVisibilityMaps(self):
        with open('visibility.txt', 'w') as output_file:
            wr = csv.writer(output_file)
            for x in np.arange(0, self.nX / self.visibility_cell_width):
                for y in np.arange(0, self.nY / self.visibility_cell_width):
                    v_map = self.visibility_cell[int(x)][int(y)].v_map
                    for a in np.arange(0, len(v_map)):
                        for b in np.arange(0, len(v_map[a])):
                            print(v_map[a][b])
                            output = [x, y, a, b, v_map[a][b]]
                            wr.writerow(output)
                            
    def loadVisibilityMaps(self):
        with open('visibility.txt', 'r') as input_file:
            r = csv.reader(input_file)
            v_map = []
            v_map_row = []
            x_tracker = 0
            y_tracker = 0
            a_tracker = 0
            b_tracker = 0
            for row in r:
                if row:
                    b_tracker += 1
                    v_prob = float(row[4])
                    v_map_row.append(v_prob)
                    if b_tracker == 12:
                        v_map.append(v_map_row)
                        v_map_row = []
                        a_tracker += 1
                        b_tracker = 0
                        if a_tracker == 12:
                            self.visibility_cell[x_tracker][y_tracker].setMap(v_map)
                            v_map = []
                            y_tracker += 1
                            a_tracker = 0
                            if y_tracker == len(self.visibility_cell[0]):
                                y_tracker = 0
                            if x_tracker == len(self.visibility_cell):
                                x_tracker = 0 # NEEDS FIXING: NOT ALL V_MAPS ARE SAVED

class Cell(object):
    """
    Cell is a base class providing an interface for all subsequent (inherited)
    cell objects.
    """
    pass

class TerrainCell(Cell):
    """
    Represents a terrain cell.
    """
    def setElevation(self, Z):
        self.Z = Z

class VisibilityCell(Cell):
    """
    Represents a visibility cell.
    """
    def __init__(self, x_ctr, y_ctr):
        self.x_ctr = x_ctr
        self.y_ctr = y_ctr
        
    def setMap(self, v_map):
        self.v_map = v_map

class EnvironmentObject(object):
    """
    EnvironmentObject is a base class providing an interface for all 
    subsequent (inherited) environment objects.
    """
    pass