import numpy as np
import copy
from scipy import *
from pylab import *
#import matplotlib as plt
import copy
from uncertainties import ufloat
from uncertainties.umath import *
from random import randrange

#--------#
# Inputs #
#--------#

turbine_pos = [[10306820.0, 6521980.0], [10306880.0, 6521980.000000001], [10307015.352636296, 6521980.0], [10307249.81204049, 6522019.777786839], [10306949.773103304, 6521980.0], [10307080.396900369, 6521980.0], [10307144.728984267, 6521980.0], [10307305.986395277, 6522059.745854174], [10307204.728695277, 6521980.186222278], [10307309.722520936, 6521980.0], [10307399.018400338, 6522145.558451642], [10307437.436389908, 6522440.0], [10307351.065846406, 6522099.977936474], [10307429.888973614, 6521980.0], [10307467.975785332, 6522260.363448672], [10307517.982694713, 6522440.0], [10307535.499018552, 6521980.0], [10307437.182277724, 6522200.0897330195], [10307492.112918809, 6522329.877738784], [10307592.39882156, 6522440.0], [10307615.538455574, 6521980.0], [10307679.667325482, 6522099.122343218], [10307755.339273604, 6522261.765437375], [10307660.0, 6522440.0], [10307645.505000647, 6522045.075373562], [10307710.686720446, 6522150.481832468], [10307769.615755491, 6522320.04993334], [10307720.0, 6522440.0], [10307780.0, 6521980.0], [10307735.19490252, 6522205.248145211], [10307780.0, 6522380.0], [10307780.0, 6522440.0]]
substation_location = [[10306800, 6521900]]
Cap = 10                                        # Capacity of cables (in number of turbines)

# Info from mesh file

site_x = 1000.
site_y = 500.
site_x_start = 1.03068e+07 
site_y_start = 6.52246e+06 - site_y

  


#def OptimiseCableLayout(turbine_pos, substation_location):

  

Tufloat = []
e = 0.1
for i in range(len(turbine_pos)):
    Tufloat.append([ufloat((turbine_pos[i][0], e)), ufloat((turbine_pos[i][1], e))])

turbine_pos = Tufloat

Sufloat = []
e = 0.1
for i in range(len(substation_location)):
    Sufloat.append([ufloat((substation_location[i][0], e)), ufloat((substation_location[i][1], e))])

substation_location = Sufloat


#------------------#
# Useful Functions #
#------------------#

def make_graph_no_depot(Rgraph,Vd):
    '''Produces a dictionary representing the graph of the form (vertex: [connected vertices], ...) removes the depot so as to seperate the routes from one another'''
    remove_list=[]
    for edge in Rgraph:
        if edge[0] in Vd or edge[1] in Vd:
            remove_list.append(edge)
    for edge in remove_list: 
        Rgraph.remove(edge)
    vertices = []
    for a_tuple in Rgraph:
        vertices.extend(list(a_tuple))
    vertices = list(set(vertices))
    nVertices = len(vertices)
    G = {}
    for i in range(0,nVertices):
        G[vertices[i]]=[]
    for edge in Rgraph:
        G[edge[1]].append(edge[0])
        G[edge[0]].append(edge[1])
    for vertex in G:
        G[vertex] = list(set(G[vertex]))
    return G
    
def make_graph_depot(Rgraph,Vd):
    '''Produces a dictionary representing the graph of the form (vertex: [connected vertices], ...)'''
    vertices = []
    for a_tuple in Rgraph:
        vertices.extend(list(a_tuple))
    vertices = list(set(vertices))
    nVertices = len(vertices)
    G = {}
    for i in range(0,nVertices):
        G[vertices[i]]=[]
    for edge in Rgraph:
        G[edge[1]].append(edge[0])
        G[edge[0]].append(edge[1])
    for vertex in G:
        G[vertex] = list(set(G[vertex]))
    return G

def find_path_length(graph, start, end, path=[]):
    '''Returns a list of vertices on a path in order that they are connected'''
    path = path + [start]
    if start == end:
        return path
    if not graph.has_key(start):
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path_length(graph, node, end, path)
            if newpath: return newpath
    return None

def construct_cost_matrix(turbine_pos, substation_location):
    '''Constructs a matrix of costs for every potential edge - connections of vertices to themselves are set to infinity'''
    coord_list = substation_location + turbine_pos
    distances = []
    grouped_distances = []
    for i in range(len(coord_list)):
        for j in range(len(coord_list)):
            if i == j:
                dist = np.inf
            else:
                dist = (sqrt((coord_list[i][0] - coord_list[j][0])**2 + (coord_list[i][1] - coord_list[j][1])**2))
            distances.append(dist)
    for i in range(0, len(distances), len(coord_list)):
        grouped_distances.append(tuple(distances[i:i+len(coord_list)]))
    C = np.array(grouped_distances)
    return C
       
def plot_output(turbine_pos, substation_location, R, C):
    '''Displays a plot of the turbines, substation and routing'''
    coord_list = substation_location + turbine_pos
    routing_length = find_routing_distance(R, C)
    title('Total distance = %s' % (str(routing_length)))
    for i in range(len(R)):
        x_coords = []
        y_coords = []
        plt.plot(coord_list[i][0].nominal_value, coord_list[i][1].nominal_value, 'k-o')
        x_coords.append(coord_list[R[i][0]][0].nominal_value), y_coords.append(coord_list[R[i][0]][1].nominal_value)
        x_coords.append(coord_list[R[i][1]][0].nominal_value), y_coords.append(coord_list[R[i][1]][1].nominal_value)
        plt.plot(x_coords, y_coords, 'k-o')
    plt.plot([site_x_start, site_x_start + site_x, site_x_start + site_x, site_x_start, site_x_start], [site_y_start, site_y_start, site_y_start + site_y, site_y_start + site_y, site_y_start], linestyle = '--', color = 'r')
    for i in range(len(substation_location)):
        plt.text(coord_list[i][0].nominal_value, coord_list[i][1].nominal_value, '  Substation')
    for i in range(len(substation_location), len(turbine_pos) + len(substation_location)):
        plt.text(coord_list[i][0].nominal_value, coord_list[i][1].nominal_value, '%s' % (str(i)))
    x_extremities = []
    for i in range(len(coord_list)):
        x_extremities.append(coord_list[i][0].nominal_value)
    x_extremities.append(site_x_start), x_extremities.append(site_x_start + site_x)
    plt.xlim(min(x_extremities)+(min(x_extremities)-max(x_extremities))*0.05, max(x_extremities)+(max(x_extremities)-min(x_extremities))*0.05)
    y_extremities = []
    for i in range(len(coord_list)):
        y_extremities.append(coord_list[i][1].nominal_value)
    y_extremities.append(site_y_start), y_extremities.append(site_y_start + site_y)
    plt.ylim(min(y_extremities)+(min(y_extremities)-max(y_extremities))*0.05, max(y_extremities)+(max(y_extremities)-min(y_extremities))*0.05)
    plt.show()
    
def find_routing_distance(R, C):
    '''Finds the sum of the edges in the final routing'''
    routing_length = []
    for i in range(len(R)):
        routing_length.append(C[R[i][0], R[i][1]])
    return sum(routing_length)
    
    

#------------------------------#
# Test 'Subject to' Conditions #
#------------------------------#
    
def neighbour_depot(edge, R, Vd):
    '''Ensures that k is neighbouring a depot - ensures no short-circuiting'''
    nhbrDepot = False
    for depot in Vd:        
        if (edge[0], depot) in R:
            nhbrDepot = True
        if (depot, edge[0]) in R:
            nhbrDepot = True
    return nhbrDepot

def K_D(edge, R, Vd):
    '''Defines the edge whose removal is proposed'''
    for depot in Vd:
        if (edge[0],depot) in R:
            k_d = (edge[0],depot)
        elif (depot,edge[0]) in R:
            k_d = (depot,edge[0])
    return k_d
    
def one_neighbour(edge, R):
    '''Prevent route branching by checking that u has only one neighbour'''
    oneNhbr = True
    for edge_temp in R:
        if edge_temp[1] == edge [1]:
            oneNhbr = False
    return oneNhbr
    
def below_capacity(edge, R, Vd, Vc, Cap, k_d):
    '''Determines whether all the routes in the proposed new routing graph remain below capacity'''
    belowCapacity = True
    R_temp = copy.deepcopy(R)
    R_temp.remove(k_d)
    R_temp.append((edge[0], edge[1]))
    G_temp = make_graph_depot(R_temp, Vd)
    for depot in Vd:
        for client in Vc:
            path_length = find_path_length(G_temp, depot, client)
            if not (path_length==None):
                if len(path_length)  > Cap:
                    belowCapacity = False
    return belowCapacity
    
def ccw(A,B,C):
    '''Checks whether 3 points in a given order are counter-clockwise from each other'''
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
    '''Checks whether a line segment linking points A & B crosses one linking points C & D'''
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def cross_edges(R, turbine_pos, substation_location, k_d, edge):
    '''Determines if any edges in the proposed new routing graph cross each other'''
    coord_list = substation_location + turbine_pos
    R_temp = copy.deepcopy(R)
    R_temp.remove(k_d)
    R_temp.append((edge[0], edge[1]))
    CrossEdges = False
    for i in range(len(R)):
        a = coord_list[R_temp[i][0]]
        b = coord_list[R_temp[i][1]]
        for j in range(len(R)):
            c = coord_list[R_temp[j][0]]
            d = coord_list[R_temp[j][1]]           
            CrossEdges = intersect(a,b,c,d)                      
            if CrossEdges:
                return CrossEdges   
    return CrossEdges
    

def cross_edges02(R, turbine_pos, substation_location, k_d, edge):
    '''Determines if any edges in the proposed new routing graph cross each other'''
    coord_list = substation_location + turbine_pos
    R_temp = copy.deepcopy(R)
    R_temp.remove(k_d)
    R_temp.append(edge)
    CrossEdges = False
    for i in range(len(R)):
        a = coord_list[R_temp[i][0]]
        b = coord_list[R_temp[i][1]]
        for j in range(len(R)):
            c = coord_list[R_temp[j][0]]
            d = coord_list[R_temp[j][1]]           
            CrossEdges = intersect02(a,b,c,d)                      
            if CrossEdges:
                return CrossEdges   
    return CrossEdges

def intersect02(A,B,C,D):
    '''Checks whether a line segment linking points A & B crosses one linking points C & D'''
    loc = []
    loc.append(A), loc.append(B), loc.append(C), loc.append(D) 
    intersects = True
    for i in range(len(loc)):
        for j in range(i+1, len(loc)):
            if loc[i] == loc[j]:
                intersects = False
                return intersects     
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)    
    
    
    
def perform_merge(edge, R, Vd, k_d):
    '''Removes the superfluous old edge and inserts the new edge & updates the routing graph'''
    R.remove(k_d)
    R.append((edge[0], edge[1]))
    Rgraph = copy.deepcopy(R)
    G = make_graph_no_depot(Rgraph, Vd)
    return G
			                                                                             


#-------#
# POSH1 #
#-------#

def initialise_R(C, Vd, Vc):
    '''produce the initial edge set - all clients connected to their nearest depot'''
    R = []
    # For each client vertex, identify the nearest depot and add (v,d) to initial edge list R
    for index in Vc:
        R.append((index, Vd[np.argmin(C[index, Vd])]))
    return R

def initialise_G(R, Vd):
    '''produce the graph of the initial edge set'''
    G = []
    Rgraph = copy.deepcopy(R)
    G = make_graph_no_depot(Rgraph, Vd)
    return G


def POSH1(Vc, Vd, R, C, G, Cap):
    '''first routing optimisation pass'''
    S = []    
    # For each possible pair of clients in the graph, calculate the cost saving from joining with edge, and add to list S
    for vertex1 in Vc:
        for vertex2 in Vc:
            if not vertex1 == vertex2:
                depot = [j[1] for i, j in enumerate(R) if j[0] == vertex1]
                saving = C[vertex1, depot] - C[vertex1, vertex2]
                S.append((vertex1, vertex2, saving))    
    # Sort the list S of cost savings in decreasing order
    S.sort(key = lambda s:s[2], reverse = True)
    
    # Iterate over list S merging two paths when allowed    
    while (not S == []) and (S[0][2][0] > 0):
        # Consider next element of S
        edge = (S[0][0],S[0][1]) # edge = (k, u)
        # if: (k,u) are not already in the same path...
        if (find_path_length(G, edge[0], edge[1])==None):
            # check that k is currently attached to a depot (i.e. merge will not create short circuit)
            if neighbour_depot(edge, R, Vd):
                # check that u has only one neighbour (i.e. merge will not create branch)
                if one_neighbour(edge, R):
                    # check that merge will not push R over capacity
                    if below_capacity(edge, R, Vd, Vc, Cap, K_D(edge, R, Vd)):
                        # check the merge will not propose two routes that are in chi (edges do not cross)
                        if not cross_edges(R, turbine_pos, substation_location, K_D(edge, R, Vd), edge):
                            G = perform_merge(edge, R, Vd, K_D(edge, R, Vd))                        
                            del S[0]
                        else: del S[0]
                    else: del S[0]
                else: del S[0]
            else: del S[0]
        else: del S[0]
    return G



#-----------------------------#
# Improve on POSH1 with POSH2 #
#-----------------------------#
 
def listroutes(R, Vd, Vc):
    '''makes a list of the routes in the routing, each route listed as a set of vertices in order from depot to end of route'''
    G = make_graph_depot(R, Vd)
    end_vertices = []

    for i in range(len(Vc+Vd)):
        A = 0    
        for j in range(len(R)):
            if R[j][0] == i:
                A += 1
            if R[j][1] == i:
                A += 1
        if A == 1 and i not in Vd:
            end_vertices.append(i)
            
    list_routes = []
    for i in range(len(end_vertices)):
        for j in range(len(Vd)):
            path_length = find_path_length(G, Vd[j], end_vertices[i])
            if path_length is not None:        
                list_routes.append(path_length)    
    return list_routes
        
def produce_S2(list_routes, C):
    '''produces another list of savings by connecting first clients in routes to last clients in other routes, or last clients to other last clients'''
    S2 = []
    end_start_depot = []
    for i in range(len(list_routes)):
        end_start_depot.append((list_routes[i][len(list_routes[i])-1],list_routes[i][1], list_routes[i][0]))
    # Savings from connecting last client (X) to first client (A), saving connection from A to its depot, Da
    for i in range(len(end_start_depot)):
        for j in range(len(end_start_depot)):
            if not i == j:
                A = end_start_depot[i][1]
                Da = end_start_depot[i][2]
                X = end_start_depot[j][0]
                saving = C[A, Da] - C[A, X]
                S2.append((A, X, saving))
    # Savings from connecting last client of one route (X1) to the last client of another route (X2), saving connection of A1 to its depot Da1
    for i in range(len(end_start_depot)):
        for j in range(len(end_start_depot)):
            if not i == j:
                X1 = end_start_depot[i][0]
                A1 = end_start_depot[i][1]
                Da1 = end_start_depot[i][2]
                X2 = end_start_depot[j][0]
                saving = C[A1, Da1] - C[X1, X2]
                S2.append((X1, X2, saving))
    remove_list = []        
    for i in range(len(S2)):
        if S2[i][2] <= 0:
            remove_list.append(S2[i])
    for savings in remove_list:
        S2.remove(savings)

    
    # Sort the list S of cost savings in decreasing order
    S2.sort(key = lambda s:s[2], reverse = True)
    return S2

def K_D2(list_routes, edge):
    '''defines the connection to be saved'''
    for i in range(len(list_routes)):    
        if edge[0] in list_routes[i]:
            k = list_routes[i][1]
            d = list_routes[i][0]          
            k_d2 = (k, d)
            return k_d2

def POSH2(R, C, Vd, Vc, Cap, G):
    '''Second pass at optimising routing, built upon POSH1 solution'''
    list_routes = listroutes(R, Vd, Vc)
    S2 = produce_S2(list_routes, C)
    
    while not (S2 == []):
        i = randrange(len(S2))
        edge = (S2[i][0],S2[i][1])
        edge1 = (S2[0][1],S2[0][0])
        if K_D2(list_routes, edge) in R:
            if one_neighbour(edge, R):
                if below_capacity(edge, R, Vd, Vc, Cap, K_D2(list_routes, edge)):
                    if not cross_edges02(R, turbine_pos, substation_location, K_D2(list_routes, edge), edge):                    
                        G = perform_merge(edge, R, Vd, K_D2(list_routes, edge))  
                        list_routes = listroutes(R, Vd, Vc)
                        S2 = produce_S2(list_routes, C)
                    else: del S2[0]                        
                else: del S2[0]
            else: del S2[0]
        elif K_D2(list_routes, edge) in R:
            edge = edge1
            if one_neighbour(edge, R):
                if below_capacity(edge, R, Vd, Vc, Cap, K_D2(list_routes, edge)):
                    if not cross_edges02(R, turbine_pos, substation_location, K_D2(list_routes, edge), edge):                    
                        G = perform_merge(edge, R, Vd, K_D2(list_routes, edge))  
                        list_routes = listroutes(R, Vd, Vc)
                        S2 = produce_S2(list_routes, C)
                    else: del S2[0]                      
                else: del S2[0]
            else: del S2[0]
        else: del S2[0]    
    return G, R    



#-------------#
# Run Program #
#-------------#

C = construct_cost_matrix(turbine_pos, substation_location)                                    # complete nxn matrix of costs
Vc = range(len(substation_location), len(turbine_pos) + len(substation_location))			# client vertex indices
Vd = range(len(substation_location))			                                            # depot vertex indices
R = initialise_R(C, Vd, Vc)
global G
G = initialise_G(R, Vd)

nturbine = len(turbine_pos) + 1          # Number of turbines (plus substation) in array
maxTsteps = 100                          # Temperature is lowered not more than maxTsteps
Tstart = 20                              # Starting temperature - has to be high enough
fCool = 0.9                              # Factor to multiply temperature at each cooling step
maxSteps = 100*nturbine                  # Number of steps at constant temperature
maxAccepted = 10*nturbine                # Number of accepted steps at constant temperature    

G = POSH1(Vc, Vd, R, C, G, Cap) 

def current_solution(R, C, Vd, Vc, Cap, G):
    '''find a randomly generated solution'''
    R_temp = copy.deepcopy(R)        
    A = POSH2(R_temp, C, Vd, Vc, Cap, G)
    Ar = A[1]
    Arouting_length = find_routing_distance(Ar, C)
    return Arouting_length, Ar, A
    
def neighbour_solution(R, C, Vd, Vc, Cap, G):
    '''find another randomly generated solution'''        
    R_temp = copy.deepcopy(R)
    B = POSH2(R_temp, C, Vd, Vc, Cap, G)
    Br = B[1]
    Brouting_length = find_routing_distance(Br, C)
    return Brouting_length, Br, B
    
def neighbour_two(Ar, C, Vd, G):
    '''An experiment in neighbour choice'''
    Rtemp = copy.deepcopy(Ar)
    Br = []
    for i in range(len(Rtemp)):
        Br.append([Rtemp[i][0], Rtemp[i-1][1]])
    i = randrange(len(Br)-1)
    j = randrange(len(Br)-1)
    if i == j:
        j += 1
        if j > len(Br):
            j -= 2
    Br[i][1], Br[j][1] = Br[j][1], Br[i][1]
    Brouting_length = find_routing_distance(Br, C)
    B = make_graph_depot(Br, Vd)
    return Brouting_length, Br, B
    
def anneal(R, C, Vd, Vc, Cap, nturbine, Tstart, fCool, maxSteps, maxAccepted, G):
    '''Performs simulated annealing'''    
    steps = 0
    accepted = 0
    graph = []
    Arouting = current_solution(R, C, Vd, Vc, Cap, G)
    Arouting_length = Arouting[0]
    Brouting = neighbour_solution(R, C, Vd, Vc, Cap, G)
    Brouting_length = Brouting[0]
    T = Tstart    
    while (T > 0) and (steps < maxSteps) and (accepted < maxAccepted):
        graph.append([steps, Arouting_length.nominal_value])
        if Arouting_length >= Brouting_length:
            steps += 1
            Arouting = Brouting; Arouting_length = Arouting[0]
            Brouting = neighbour_solution(R, C, Vd, Vc, Cap, G); Brouting_length = Brouting[0]  
        elif Arouting_length < Brouting_length:
            steps += 1
            if (((Arouting_length - Brouting_length) / T) < 100) and (exp((Arouting_length - Brouting_length) / T) > (randrange(1)*0.05)):            
                steps += 1
                Arouting = Brouting; Arouting_length = Arouting[0]
                Brouting = neighbour_solution(R, C, Vd, Vc, Cap, G); Brouting_length = Brouting[0]
            else:
                steps += 1
                accepted += 1 
                Brouting = neighbour_solution(R, C, Vd, Vc, Cap, G); Brouting_length = Brouting[0]
        else: steps += 1
        T *= fCool
    return Arouting
    

plot_output(turbine_pos, substation_location, R, C)


outs = []
#print graph
i=0
while i in range(20):
    out = anneal(R, C, Vd, Vc, Cap, nturbine, Tstart, fCool, maxSteps, maxAccepted, G)
    print out[0]
    plot_output(turbine_pos, substation_location, out[1], C)
    outs.append(out)
    i+=1

outs.sort(key = lambda row: row[0])

plot_output(turbine_pos, substation_location, outs[0][1], C)        
      
    
    
    
#    G = POSH1(Vc, Vd, R, C, G, Cap)
##    print R
##    plot_output(turbine_pos, substation_location, R, C)
#    G = POSH2(R, C, Vd, Vc, Cap)
#    print R
#    plot_output(turbine_pos, substation_location, R, C)
#    return R
    
#OptimiseCableLayout(turbine_pos, substation_location)

#derivative = (OptimiseCableLayout(turbine_pos, substation_location)).derivatives[turbine_pos[0][0]]
#
#print derivative
    
