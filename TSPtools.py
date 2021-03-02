# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 22:01:45 2021

@author: Hamidmo
"""

def distance_uv(u, v, is_u_prime, is_u_tenth): 
    import math
    # apply 1.1 factor for edge (u,v) length unless u is prime; 
    CstFactor = 1.00 if  not is_u_tenth or is_u_prime else 1.10
    return math.sqrt((v[1]-u[1])**2 + (v[0]-u[0])**2) * CstFactor


def distxyfun(x1,y1,x2,y2): 
    import math
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def ComputeDistMatrix(cities):  #computeDist_xy
    import pandas as pd
    
    rows_list = [] 
    m = cities.shape[0]
    for i in range(0,m-1):
        for j in range(i+1,m):  
            dict1 = {}
            dict1.update( u=int(cities["CityId"][i]) , 
                          v=int(cities["CityId"][j]) ,
                          dist_uv=distxyfun(cities["X"][i],cities["Y"][i],
                                              cities["X"][j],cities["Y"][j]) )
            rows_list.append(dict1)          
            
    return pd.DataFrame(rows_list)
   
 
 
def calcCircuitCost(circuit,City_dict):   
    #link i,j
    total_dist = 0.0 
    i = circuit[0]
    u = [City_dict['X'][i], City_dict['Y'][i] ]  
    
    for stp in range(len(circuit)-1):
        is_u_prime = City_dict['IsPrime'][i]              
        j = circuit[stp+1]
        v = [ City_dict['X'][j], City_dict['Y'][j] ]
        total_dist += distance_uv(u, v ,is_u_prime,(stp % 10) == 0)
        u = v
        i=j
        
    return total_dist



def isprime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if (n % i) == 0:  return False
    return True

            

def  Kruskal(this_u, this_v ,  W ):
    tree_u = -1
    tree_v = -1
    #u,v each belong to exactly one W_i
    for i in range(len(W)): 
        if (this_u in W[i]): tree_u = i  
        if (this_v in W[i]): tree_v = i 
        if ( tree_v > -1) and (tree_u > -1): break
    
    if ( (tree_v == tree_u) and (tree_u > -1 ) ):
        return False #impossible to avoid loop in this case.
    elif (tree_v > -1) and (tree_u > -1):
        W[tree_u] = list(set().union(W[tree_u],W[tree_v]))
        W.remove(W[tree_v])
        return True 
 
 
def SortHyperGraph(HyperGraph, StartPoint): 
     
    source = False
    sink = False
    for i in range(len(HyperGraph)):
        if (source and sink):
            break
        if (HyperGraph[i][0] == StartPoint) or (HyperGraph[i][1] == StartPoint ):
            if (not source):
                x = HyperGraph[i]
                HyperGraph[i] = HyperGraph[0]
                HyperGraph[0] =  x
                source = True
                if ( HyperGraph[0][1] == StartPoint ):
                    HyperGraph[0][1] = HyperGraph[0][0]
                    HyperGraph[0][0] = StartPoint
            elif(not sink):       
                x = HyperGraph[i]
                HyperGraph[i]=HyperGraph[len(HyperGraph)-1]
                HyperGraph[len(HyperGraph)-1] =  x
                sink = True
    return HyperGraph

            
def Hierholzer_OnePath(HyperGraph):   
    Circ = []
    exhusted = False
    ind=0 
    #input is HG whose first vertex is to be start & end of cicuit. 
    Circ = [HyperGraph[ind][0]]
    while( (len(HyperGraph) > 0 ) and (not exhusted) ):
        exhusted = True 
        v= HyperGraph[ind][1]  
        Circ.append(v)
        HyperGraph.remove(HyperGraph[ind]) #remove walked edge
        for x in HyperGraph:        
            if ( v==x[0]  ):
                ind = HyperGraph.index(x)
                exhusted = False
                break             
            elif(v==x[1] ):
                ind = HyperGraph.index(x)
                HyperGraph[ind][1]=HyperGraph[ind][0]
                HyperGraph[ind][0]=v
                exhusted = False
                break
        #while loop terminates once a eulerian loop is found
        #print(exhusted)
    return HyperGraph,Circ,exhusted

  
            

def Hierholzer(HyperGraph):
# assumption: hypergraph is connected    
    Circ = [] 
    #first for loop wont run to get a circuit in HG starting and ending at 0 
    # as HG is already sorted for 0. 
    
    while(len(HyperGraph)>0): 
        #finding adjacent non-included vertices in hypergraph to the circuit
        #note existing HG only includes nodes which are not yet added to circuit
        for r in Circ: 
            if( (r in [HyperGraph[j][0] for j in range(len(HyperGraph)) ]) or
                  (r in [HyperGraph[j][1] for j in range(len(HyperGraph)) ]) ):
                HyperGraph = SortHyperGraph(HyperGraph, r)
                break
                        
        HyperGraph,sub_circ,exhusted =  Hierholzer_OnePath(HyperGraph)
        a = 0
        b = 0
        for j in range(len(sub_circ)):
            if sub_circ[j] in Circ:
                t= sub_circ[j]
                a = sub_circ.index(t) 
                b = Circ.index(t)
                break
        #insert the found loop to the existing path. 
        q=[z for z in range(a,len(sub_circ))] + [z for z in range(0,a)]
        sub_circ = [sub_circ[s] for s in q ]
        Circ[b:b+1] = sub_circ  
            
    return Circ;   
   


def longestEdge(ct,TSP):
    
    #City_dict = ct.to_dict()
    City = ct["CityId"].tolist()
    X    = ct["X"].tolist()
    Y    = ct["Y"].tolist()    
    max_dist = 0.0
    ret_u , ret_v = 0, 0
    r_tu, r_tv    = 0,0 
    
    for i in range(len(TSP)-1):
        u,v = TSP[i],TSP[i+1]
        u_t = City.index(u)
        v_t = City.index(v)         
        sd = distxyfun( X[u_t],Y[u_t],X[v_t],Y[v_t] ) 
    
        if max_dist<sd:
            max_dist=sd
            ret_u , ret_v = u, v
            r_tu, r_tv    = u_t,v_t 
       
#    ret_dict={"CityId":{u:u,v:v},"X":{u:X[u_t],v:X[v_t]},"Y":{u:Y[u_t],v:Y[v_t]}}
    ret_vec =  []
    ret_vec.append(  [ret_u,X[r_tu],Y[r_tu]] )
    ret_vec.append(  [ret_v,X[r_tv],Y[r_tv]] )
         
    return ret_vec    