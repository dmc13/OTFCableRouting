# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 10:11:39 2013

@author: dmc13
"""

import numpy as np
import scipy as sp
from matplotlib import pyplot as plt
import math


## USEFUL FUNCTIONS

def construct_cost_matrix(vertices):
    '''Constructs a matrix of costs for every potential edge - connections of vertices to themselves are set to infinity'''
    distances = []
    grouped_distances = []
    for i in range(len(vertices)):
        for j in range(len(vertices)):
            if i == j:
                dist = np.inf
            else:
                dist = (np.sqrt((vertices[i][0] - vertices[j][0])**2 + (vertices[i][1] - vertices[j][1])**2))
            distances.append(dist)
    for i in range(0, len(distances), len(vertices)):
        grouped_distances.append(tuple(distances[i:i+len(vertices)]))
    C = np.array(grouped_distances)
    return C
    
    
def rand_breaks(n, MinRoute, Nroutes, NBreaks):
    RB = [np.random.random_integers(MinRoute, Capacity)]
    for i in range(1, NBreaks):
        RB.append(np.random.random_integers(MinRoute, Capacity) + RB[i-1])
    if RB[-1] < (n - Capacity):
        short = (n - Capacity) - RB[-1]
        add_each = int(np.ceil(0.5 + short / len(RB)))
        for i in range(len(RB)):
            RB[i] = RB[i] + add_each * (i+1)
    RB = np.array((RB))
    return RB
    
def produce_plot(R, V, dist):
    '''display with matplotlib'''
    plt.title('Total distance='+str(dist))
    plt.plot(V[:,0],V[:,1],'o')
    for i in range(len(R)):
        plt.plot(R[i][:,0], R[i][:,1], '-')
    for i in range(len(V)):
        plt.text(V[i][0], V[i][1], '%s' % (str(i)))
    plt.axis('equal')
    plt.show()


## INPUTS

turbine_locations = [[1,2],[1,3],[1,4],[2,2],[2,3],[2,4],[3,2],[3,3],[3,4],[4,2],[4,3],[4,4],[9,9]]
substation_location = [[0,0]]

Capacity = 6

PopSize = 16

NumIter = 100000

ShowProg = False

ShowResult = False

## Process inputs ...

vertices = substation_location + turbine_locations

xy = np.array(vertices)

NRoutes = int(math.ceil(float(len(vertices)) / Capacity))
print NRoutes

MinRoute = len(vertices) / NRoutes

n = len(turbine_locations)

DMat = construct_cost_matrix(vertices)

NBreaks = NRoutes - 1



## INITIALISE POPULATION

PopRoute = np.zeros((PopSize, n), dtype = int)
PopBreaks = np.zeros((PopSize, NBreaks), dtype = int)

PopRoute[0] = range(1, n+1)
PopBreaks[0] = rand_breaks(n, MinRoute, NRoutes, NBreaks)
for i in range(1, PopSize):
    PopRoute[i] = np.random.permutation(n) + 1
    PopBreaks[i] = rand_breaks(n, MinRoute, NRoutes, NBreaks)

## INITIALISE GENETIC ALGORITHM

GlobalMin = np.inf
TotalDist = np.zeros((1, PopSize))
DistHistory = np.zeros((1, NumIter))
TempPopRoute = np.zeros((8, len(turbine_locations)), dtype = int)
TempPopBreaks = np.zeros((8, NBreaks), dtype = int)
NewPopRoute = np.zeros((PopSize, len(turbine_locations)), dtype = int)
NewPopBreaks = np.zeros((PopSize, NBreaks), dtype = int)



for i in range(NumIter):
    for p in range(PopSize):
        d = 0
        pRoute = PopRoute[p].tolist()
        pBreak = PopBreaks[p].tolist()
        rting = [[0] + pRoute[0:pBreak[0]]]
        if len(pBreak) > 1:
            for f in range(1, len(pBreak)):
                rting.append([0] + pRoute[pBreak[f-1]:pBreak[f]])
        rting.append([0] + pRoute[pBreak[-1]:])
        for r in range(len(rting)):
            for v in range(len(rting[r]) - 1):
                d = d + DMat[v][v+1]
        TotalDist[0][p] = d  
    MDidx = np.argmin(TotalDist)
    MinDist = TotalDist[0][MDidx]
    DistHistory[0][i] = MinDist
    if MinDist < GlobalMin:
        GlobalMin = MinDist
        OptRoute = PopRoute[MDidx]
        OptBreak = PopBreaks[MDidx]
        
    RandomOrder = np.random.permutation(n)
    for p in range(8, PopSize+1, 8):
        rtes = PopRoute[RandomOrder[p-8:p]]
        brks = PopBreaks[RandomOrder[p-8:p]]
        dists = TotalDist[0][RandomOrder[p-8:p]]
        idx = np.argmin(dists)    
        bestof8Route = rtes[idx]
        bestof8Break = brks[idx]
        selector = np.random.permutation(n)
        randlist = [selector[n/3], selector[2*n/3]]
        I = min(randlist)
        J = max(randlist)
        for k in range(8):
            TempPopRoute[k] = bestof8Route
            TempPopBreaks[k] = bestof8Break
        # Transformation 1        
        Temp = TempPopRoute[1][I]; TempPopRoute[1][I:J] = TempPopRoute[1][J:I:-1]; TempPopRoute[1][J] = Temp
        # Transformation 2        
        TempPopRoute[2][I], TempPopRoute[2][J] = TempPopRoute[2][J], TempPopRoute[2][I]
        # Transformation 3        
        TempPopRoute[3] = np.array(TempPopRoute[3].tolist()[0:I] + TempPopRoute[3].tolist()[I+1:J] + [TempPopRoute[3].tolist()[I]] + TempPopRoute[3].tolist()[J:])
        # Transformation 4
        TempPopBreaks[4] = rand_breaks(n, MinRoute, NRoutes, NBreaks)
        # Transformation 5        
        Temp = TempPopRoute[5][I]; TempPopRoute[5][I:J] = TempPopRoute[5][J:I:-1]; TempPopRoute[5][J] = Temp
        TempPopBreaks[5] = rand_breaks(n, MinRoute, NRoutes, NBreaks)
        # Transformation 6        
        TempPopRoute[6][I], TempPopRoute[6][J] = TempPopRoute[6][J], TempPopRoute[6][I]
        TempPopBreaks[6] = rand_breaks(n, MinRoute, NRoutes, NBreaks)
        # Transformation 7        
        TempPopRoute[7] = np.array(TempPopRoute[7].tolist()[0:I] + TempPopRoute[7].tolist()[I+1:J] + [TempPopRoute[7].tolist()[I]] + TempPopRoute[7].tolist()[J:])
        TempPopBreaks[7] = rand_breaks(n, MinRoute, NRoutes, NBreaks)        
        
        NewPopRoute[p-8:p] = TempPopRoute
        NewPopBreaks[p-8:p] = TempPopBreaks
       
    PopRoute = NewPopRoute
    PopBreaks = NewPopBreaks
       

OptRoute = OptRoute.tolist()
OptBreak = OptBreak.tolist()
rting = [[0] + OptRoute[0:OptBreak[0]]]
if len(OptBreak) > 1:
    for f in range(1, len(OptBreak)):
        rting.append([0] + OptRoute[OptBreak[f-1]:OptBreak[f]])
rting.append([0] + OptRoute[OptBreak[-1]:])

print [0] + OptRoute[OptBreak[-1]:OptRoute[-1]]
print OptRoute[OptBreak[-1]:]
print OptRoute[OptBreak[-1]:OptRoute[-1]], 'eh?'
print OptRoute
print OptBreak
print rting



V = np.array((vertices))

for i in range(len(rting)):
    for j in range(len(rting[i])):
        rting[i][j] = vertices[rting[i][j]]
    rting[i] = np.array(rting[i]) 
    
R = np.array((rting))
    
produce_plot(R, V, GlobalMin)



























