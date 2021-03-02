# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 23:24:52 2021

@author: HamidMo
"""

import random,math
import pandas as pd

def isprime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if (n % i) == 0:  return False
    return True
   
def distance_uv(u, v, is_u_prime, is_u_tenth): 
    # apply 1.1 factor for edge (u,v) length unless u is prime; 
    CstFactor = 1.00 if  not is_u_tenth or is_u_prime else 1.10
    return math.sqrt((v[1]-u[1])**2 + (v[0]-u[0])**2) * CstFactor


class ACO(object):
    def __init__(self, ant_count: int, generations: int, alpha: float, beta: float, rho: float, q: int,
                 strategy: int, ct: pd.DataFrame, City_dict: dict):
        """
        :param strategy: pheromone update strategy. 0 - ant-cycle, 1 - ant-quality, 2 - ant-density
        """
        self.Q = q
        self.rho = rho
        self.beta = beta
        self.alpha = alpha
        self.ant_count = ant_count
        self.generations = generations
        self.update_strategy = strategy
        self.ct=ct
        self.City_dict=City_dict
        self.N = len(ct)
        self.PopularLinks = {"u":{},'v':{},"pheromone":{}}

    def warmstart(self, goodpaths):
        
        U = []
        V = [] 
        UV= [] 
        
        for p in goodpaths:
            NrLinks = len(self.PopularLinks["pheromone"])             
            p_total_cost = self._calcCircuitCost(p)
         
            for stp,vtx in enumerate(p):
                if stp>=len(p)-1: continue                
                if ([vtx,p[stp+1]] in UV):
                    w= U.index(vtx)
                    self.PopularLinks['pheromone'][w] += self.Q/p_total_cost
                elif ([p[stp+1],vtx] in UV):  
                    w= V.index(vtx)
                    self.PopularLinks['pheromone'][w] += self.Q/p_total_cost 
                else:
                    y= len(self.PopularLinks['u'])  
                    self.PopularLinks['u'][y] = vtx
                    self.PopularLinks['v'][y] = p[stp+1]
                    self.PopularLinks['pheromone'][y] = 1.0/(self.N**1)
                    self.PopularLinks['pheromone'][y] += self.Q/p_total_cost 
                    U.append(vtx)
                    V.append(p[stp+1])
                    UV.append([vtx,p[stp+1]])
        
        

    def _calcCircuitCost(self,circuit):   
        #link i,j
        total_dist = 0.0 
        i = circuit[0]
        u = [self.City_dict['X'][i], self.City_dict['Y'][i] ]  
        
        for stp in range(len( circuit )-1):
            is_u_prime = self.City_dict['IsPrime'][i]              
            j = circuit[stp+1]
            v = [ self.City_dict['X'][j], self.City_dict['Y'][j] ]
            total_dist += distance_uv(u, v ,is_u_prime,(stp % 10) == 0)
            u = v
            i=j
            
        return total_dist
    
    
    def _getlink_pheromone(self, i,j,gen):
        #potential improvements
        U = [*self.PopularLinks["u"].values()]
        V = [*self.PopularLinks["v"].values()]
        UV=[[U[i],V[i]] for i in range(len(V))]  
        if ([i,j] in UV):
            w= U.index(i)
            return self.PopularLinks['pheromone'][w]  
        elif ([j,i] in UV):    
            w= V.index(i)
            return self.PopularLinks['pheromone'][w]  
        else:
            return self.rho**gen / (self.N**2)
######
    def _update_pheromone(self, ants: list,gen:int):
        #only used and new links are kept
        NrLinks = len(self.PopularLinks["pheromone"])
        for i in range(NrLinks): 
             self.PopularLinks["pheromone"][i] *= self.rho
        
        U = [*self.PopularLinks["u"].values()]
        V = [*self.PopularLinks["v"].values()] 
        UV=[[U[i],V[i]] for i in range(len(V))] 
        
        for ant in ants:
            for i,vtx in enumerate(ant.path):
                if i>=len(ant.path)-1: continue                
                if ([vtx,ant.path[i+1]] in UV):
                    w= U.index(vtx)
                    self.PopularLinks['pheromone'][w] += self.Q/ant.total_cost
                elif ([ant.path[i+1],vtx] in UV):  
                    w= V.index(vtx)
                    self.PopularLinks['pheromone'][w] += self.Q/ant.total_cost 
                else:
                    y= len(self.PopularLinks['u'])  
                    self.PopularLinks['u'][y] = vtx
                    self.PopularLinks['v'][y] = ant.path[i+1]
                    self.PopularLinks['pheromone'][y] = self.rho**gen/(self.N**2)
                    self.PopularLinks['pheromone'][y] += self.Q/ant.total_cost 
                    U.append(vtx)
                    V.append(ant.path[i+1])
                    UV.append([vtx,ant.path[i+1]])
                    
        #trimming forgotten links
#        NrLinks = len(self.PopularLinks["pheromone"])
#        if NrLinks>self.N**(1.5):
#            mn = np.mean(list(self.PopularLinks["pheromone"].values()))
#            threshold = mn / self.N**2 
#        
#            for i in range(NrLinks): 
#                 if (self.PopularLinks["pheromone"][i] < threshold):
#                    del self.PopularLinks["pheromone"][i]
#                    del self.PopularLinks["u"][i]
#                    del self.PopularLinks["v"][i]
#                    
#            print("Note: ", threshold , mn , NrLinks, np.mean(list(self.PopularLinks["pheromone"].values())) )
                    
 
                    
                    
    def solve(self):       
        
        best_cost = float('inf')
        best_solution = []
        for gen in range(self.generations):
            ants = [ _Ant(self) for i in range(self.ant_count)]
            for ant in ants:
                for i in range(self.N ):
                    ant._select_next(gen,i) 
                if ant.total_cost < best_cost:
                    best_cost = ant.total_cost
                    best_solution = [] + ant.path 
                
            print("PL,Gen,Best: ",len(self.PopularLinks["u"]),gen,best_cost)
            self._update_pheromone(ants,gen)
            
            # print('generation #{}, best cost: {}, path: {}'.format(gen, best_cost, best_solution))
        print("----")
        return best_solution, best_cost
    
                    
  #  def warmstart():
 #       return
    

###################################################################################################
class _Ant(object):
    def __init__(self, aco: ACO ):
        self.colony = aco
        self.N = N
        self.total_cost = 0.0
        self.path = []
        #self.pheromone_delta = []  # the local increase of pheromone
        #self.allowed = [i for i in range(N)]  # nodes which are allowed for the next selection
        #self.eta = [[0 if i == j else 1 / graph.matrix[i][j] for j in range(N)] for i in
           #         range(graph.rank)]  # heuristic information
        
        self.start = random.randint(0, N-1)  
        self.path.append(self.start)
        self.current = self.start
        self.path = [self.start]  # path
        #self.allowed.remove(start) 

    def _select_next(self,gen,step):
        if step==self.colony.N - 1:
            selected = self.start 
        else:             
        
            denominator = 0
            
            xarea,yarea = self.colony.ct['X_area'][self.current] , self.colony.ct['Y_area'][self.current] 
           
            cond1 = self.colony.ct["X_area"] >=  xarea -2
            cond2 = self.colony.ct["X_area"] <=  xarea +2
            cond3 = self.colony.ct["Y_area"] >=  yarea -2
            cond4 = self.colony.ct["Y_area"] <=  yarea +2        
            
            reachable_cities = self.colony.ct.loc[ (cond1 & cond2 & cond3 & cond4 ), "CityId" ] 
            reachable_cities = [rc for rc in  reachable_cities if (rc not in self.path) ]
            
            if len(reachable_cities) == 0:
                reachable_cities = self.colony.ct["CityId"]
                reachable_cities = [rc for rc in  reachable_cities if (rc not in self.path) ]
                
            #print("H_0", self.colony.N , len(self.path), xarea,yarea,len(reachable_cities),step)
            
        
            u = [self.colony.City_dict['X'][self.current], self.colony.City_dict['Y'][self.current]]
            is_u_prime = self.colony.City_dict['IsPrime'][self.current]  
            is_u_tenth = (step%10)==0 
            pherm=[]
            eta=[]
            for i in reachable_cities:
                pherm.append(self.colony._getlink_pheromone(self.current,i,gen))
                v = [City_dict['X'][i], City_dict['Y'][i]]
                dist = distance_uv(u, v, is_u_prime, is_u_tenth)
                t_eta=.99
                if dist > 0:  t_eta=1./ dist
                eta.append(t_eta)
                
            for i in range(len(reachable_cities)):
                denominator += pherm[i]**self.colony.alpha *  eta[i]** self.colony.beta
            
            probabilities = [0 for i in range(len(reachable_cities))]  
            
            #print("H__1",len(reachable_cities),len(probabilities))
            for i in range(len(reachable_cities)):
                try:
                    probabilities[i] = (pherm[i]**self.colony.alpha *  eta[i]** self.colony.beta) / denominator
                except ValueError:
                    pass  # do nothing
            # select next node by probability roulette
            
          #  print("H_2",len(reachable_cities),len(probabilities))
            selected = -1
            rand = random.random()
            for i, prob in enumerate(probabilities):
                rand -= prob
                if rand <= 0:
                    selected = reachable_cities[i]
                    break
       # print("H_3",selected,len(reachable_cities))
        u = [self.colony.City_dict['X'][self.current], self.colony.City_dict['Y'][self.current]]
        v = [self.colony.City_dict['X'][selected], self.colony.City_dict['Y'][selected]]
        uprime= isprime(self.current)
      
        self.path.append(selected)
      #  print("Path",self.path)
        self.total_cost += distance_uv(u, v, uprime , (step % 10)==0)
        self.current = selected

    # noinspection PyUnusedLocal
    def _update_pheromone_delta(self):
        self.pheromone_delta = [[0 for j in range(self.graph.rank)] for i in range(self.graph.rank)]
        for _ in range(1, len(self.tabu)):
            i = self.tabu[_ - 1]
            j = self.tabu[_]
            if self.colony.update_strategy == 1:  # ant-quality system
                self.pheromone_delta[i][j] = self.colony.Q
            elif self.colony.update_strategy == 2:  # ant-density system
                # noinspection PyTypeChecker
                self.pheromone_delta[i][j] = self.colony.Q / self.graph.matrix[i][j]
            else:  # ant-cycle system
                self.pheromone_delta[i][j] = self.colony.Q / self.total_cost
                
############################################################################
                ######################################################
##########################################################################
                
 
if __name__ == "__main__":  
        
    ct = pd.read_csv("cities.csv")
    #ct=ct.head(40)     
    N = ct.shape[0]
    ct["X"] = ct["X"]-ct["X"].min()
    ct["Y"] = ct["Y"]-ct["Y"].min()  
    density = min(445,N)
    World_X = ct["X"].max() + .001
    World_Y   = ct["Y"].max()  + .001
    bag_area_std =   World_X * World_Y * density/ N
    length_std = math.ceil(math.sqrt(bag_area_std) )    
    ct["X_area"] = ct.apply(lambda c: int(c["X"] // length_std),  axis=1 )
    ct["Y_area"] = ct.apply(lambda c: int(c["Y"] // length_std),  axis=1 )  
    ct["IsPrime"] = ct.apply(lambda c: isprime(c["CityId"]) , axis=1 ) 
    City_dict = ct.to_dict()
    
     
    start_time = time.time() 
    
    NrRuns = 5 
    SelPath=[]
    SelCost=[]
    for i in range(NrRuns):               
        aco = ACO(10,10, 1.0, 10.0, 0.5, 10, 2,ct,City_dict) 
        aco.warmstart(SelPath) 
        print("--- %s seconds ---" % (time.time() - start_time))
        path, cost = aco.solve() 
        SelPath.append(path)
        SelCost.append(cost)
         
        if len(SelPath) > 10:
            maxcost = max(SelCost)
            t = SelCost.index(maxcost)
            SelCost.pop(t)
            SelPath.pop(t)  
        
    
    print("--- %s seconds ---" % (time.time() - start_time))