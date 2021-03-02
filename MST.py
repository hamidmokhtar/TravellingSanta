# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 12:27:05 2021

@author: Hamidmo
"""


def MinSpanningTree(ct,dist_matrix):
    import pandas as pd
    from TSPtools import Kruskal
    
    N=ct.shape[0] 	
    
	 
	#################### DIST is calculated; now sort it for min spanning tree

    dist_matrix = dist_matrix.sort_values(by=['dist_uv'])
    #r = dist_matrix.drop_duplicates()  
 
    XY_dist = dist_matrix
    V_u = XY_dist["u"].tolist()
    V_v = XY_dist["v"].tolist()
    
#    Vrtx = ct["CityId"]    
    Vrtx = (set(V_u)).union(set(V_v))  
    V_partitions = [] 
    for i in range(len(Vrtx)):
    	a=int(Vrtx.pop() )
    	V_partitions.append([a]) 
    
    SpTre = pd.DataFrame(columns=['dist_uv','u','v' ] ) 
    SpTre.astype(dtype= {"u":"int", "v":"int","dist_uv":"double"})
    
   # print("debug0", XY_dist.shape[0] , V_partitions )
    
    while (XY_dist.shape[0] > 0) and (SpTre.shape[0] < N - 1 ):
        x = XY_dist.head(1)
        this_dist_uv = float(x["dist_uv"])
        this_u = int(x["u"])
        this_v = int(x["v"])
        XY_dist = XY_dist.iloc[1:]
        	
        rows_list = []
        if Kruskal(this_u, this_v , V_partitions ):
            
            dict1 = {}
            dict1.update( u=int(this_u),v=int(this_v), dist_uv=this_dist_uv  )
            rows_list.append(dict1)  #end if
    #        print("debug3",u,v)
            
        df = pd.DataFrame(rows_list)  
        SpTre = pd.concat([SpTre,df]) #endwhile
    
 #   print("debug", XY_dist.shape[0] , V_partitions )
    return SpTre     
    
 

def AppendMatching(ct,SpTre,dist_matrix):   
	#######perfect matching?
    import pandas as pd
 
    NodeSet = ct["CityId"]
    N= len(NodeSet)
    
    U = SpTre["u"].tolist()
    V = SpTre["v"].tolist()
    deg = [ U.count(NodeSet[i]) + V.count(NodeSet[i]) for i in range(N) ]  

    #print("debug6: ", len(SpTre), len(deg), N, len(NodeSet) ) 
    
    OddVer = [NodeSet[i] for i in range(N) if deg[i]%2==1 ] 
    
    W = set(OddVer)
    Udf = pd.DataFrame(dist_matrix["u"]) 
    Vdf = pd.DataFrame(dist_matrix["v"]) 
    cond1     = Udf.isin(W) 
    cond2     = Vdf.isin(W) 
    # using only odd-degree vertices data      
    XY_dist = dist_matrix.loc[ (cond1["u"] | cond2["v"]) , ] 
    
    XY_dist = XY_dist.sort_values(by=['dist_uv'])  
    # dist_matrix = dist_matrix.drop_duplicates()  
    
    U = XY_dist["u"].tolist()
    V = XY_dist["v"].tolist()
    distUV = XY_dist["dist_uv"].tolist()

    #this method is very inefficient... to be updated
    rows_list = []
    W = set(OddVer)
    while (len(W) > 0) and (len(distUV)>0): 
        this_dist_uv = distUV[0]
        this_u = int( U[0] )
        this_v = int( V[0] )        
        if (this_u in W) and (this_v in W):
            W.remove(this_u)
            W.remove(this_v)
            dict1 = {}
            dict1.update( u=this_u,v=this_v, dist_uv=this_dist_uv  )
            rows_list.append(dict1)   
            cond1     = Udf.isin(W) 
            cond2     = Vdf.isin(W)  
            XY_dist = dist_matrix.loc[ (cond1["u"] | cond2["v"]) , ] 
            XY_dist = XY_dist.sort_values(by=['dist_uv']) 
            U = XY_dist["u"].tolist()
            V = XY_dist["v"].tolist()
            distUV = XY_dist["dist_uv"].tolist() 
        else:
            U = U[1:] 
            distUV = distUV[1:] 
            V = V[1:]  #endif
        #print("debug9":len(W),len(distUV))
       #end while 
          
    df = pd.DataFrame(rows_list)  
    HyprGr = pd.concat([SpTre,df]) 
    
    #Hypergraph is the set of edges in which TSP path can be found using eulerian tour
    #Note that repeated edges are allowed, it is a multigraph. 
    return HyprGr

def FindEulerianTour(HyprGr):
    from TSPtools import SortHyperGraph,Hierholzer
    
    HyperGraph = HyprGr[['u','v','dist_uv']].values.tolist() 
    #s_longEdge,t_longEdge = this_u,this_v #last edge added to the circuit is the longest edge
    
    
    '''required cityId=0 to be the starting point, 
     so: SortHyperGraph called for vtx=0    '''
    HyperGraph = SortHyperGraph(HyperGraph, 0)   
    
    #Using Hierholzer algorithm, find  Eulerian circuit  
    EulerianCirc = [] 
    EulerianCirc = Hierholzer(HyperGraph) 
      
    
    Tour=[]    
    # shortcutting: remove repeated vertices
    for i in range(len(EulerianCirc)):
    	if EulerianCirc[i] in set(Tour) and i!=len(EulerianCirc)-1: 
            continue
    	else: 
            Tour.append(EulerianCirc[i]) #endif
    #endfor
            
    
    return Tour  