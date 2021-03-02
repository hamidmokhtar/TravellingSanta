# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 18:29:02 2021

@author: Hamidmo

Clustring cities for divide and conquer 
"""



import numpy as np
import pandas as pd
import math,os,time,csv

##############################################################

def intersect(St,x,y,size):
    if (St[0] >=  x) and (St[0] <  x+size):
        if (St[1] >=  y ) and (St[1] < y+size):
            return True
    if (St[0]+St[2] >  x) and (St[0] +St[2] <=  x+size):
        if (St[1] +St[2] >  y ) and (St[1] +St[2] <= y+size):
            return True
    return False
 
def covered(St,x,y,size):
    if (St[0] >= x) and (St[0] <= x+size):
        if (St[1] >= y ) and (St[1] <= y+size):
            if (St[0]+St[2] >= x) and (St[0] +St[2] <=  x+size):
                if (St[1] + St[2] >= y ) and (St[1] +St[2] <= y+size):
                    return True
    return False  

def fixlowdensity(ct,State,density):         
    
    for size in range(2,6):
        for i in range(0,k_x-size):
            for j in range(0,k_y-size):
                LowDens = []
                covering = True
                for inds in range(len(State)):
                    if intersect(State[inds],i,j,size):
                        if not covered(State[inds],i,j,size):
                            covering =False
                            break
                        else:
                            LowDens.append(State[inds]) 
                
                if covering and len(LowDens)>1:
                    DenseEnough = True
                    for ss in LowDens:
                        if ss[3]<0.9*density:
                            DenseEnough = False
                    if DenseEnough: 
                        continue
                    NewBorder =  []
                    NewBorder.append(i)
                    NewBorder.append(j)
                    NewBorder.append(size)
                    NewBorder.append( BoxPopulation(ct,NewBorder) )
                    State = [ss for ss in State if not ss in LowDens] 
                    State.append(NewBorder)        
                                 
        
    State= [State[j] for j in range(len(State)) if State[j][3]!=0 ]  
 
    return State


def BoxPopulation(ct,bag_ind): 
    cond1a =  ct["X"] >= (bag_ind[0] ) *length_std
    cond1b =  ct["X"] <= (bag_ind[0] + bag_ind[2] ) *length_std
    cond2b =  ct["Y"] >= (bag_ind[1] ) *length_std
    cond2a =  ct["Y"] <= (bag_ind[1] + bag_ind[2] ) *length_std
  #  print(cond1a,cond1b,cond2a,cond2b)
    subcities = ct.loc[ (cond1a & cond1b) & (cond2a & cond2b ) , ] 
    return subcities.shape[0]  
 

def fixlargedensity(ct,State,density):
     
    maxden = np.max( [ State[i][3] for i in range(len(State)) ] ) 
    while ( maxden > (1.5 * density)) and (len(State) < 3.5* density):
        
        for indx in range(len(State)):
            if State[indx][3]==maxden: 
                break
        
        
        cond1a =  ct["X"] >=  State[indx][0] * length_std 
        cond1b =  ct["X"] <=  (State[indx][0]+ State[indx][2] )*length_std
        cond2b =  ct["Y"] >=  State[indx][1] * length_std
        cond2a =  ct["Y"] <=  (State[indx][1]+ State[indx][2] ) * length_std
        cluster = ct.loc[ (cond1a & cond1b) & (cond2a & cond2b ) , ]
        
        xmean = cluster["X"].mean()
        ymean = cluster["Y"].mean()
        NewStep = State[indx][2]/2
         
        cond1  =  cluster["X"] <=  xmean 
        cond2  =  cluster["Y"] <=  ymean
        subclstr = cluster.loc[ cond1 & cond2 , ]
        State.append([State[indx][0],State[indx][1],NewStep, subclstr.shape[0] ])
        
        
        cond1  =  cluster["X"] <=  xmean 
        cond2  =  cluster["Y"] >  ymean
        subclstr = cluster.loc[ cond1 & cond2 , ]
        State.append([State[indx][0],State[indx][1]+NewStep,NewStep, subclstr.shape[0] ])
         
        cond1  =  cluster["X"] >  xmean 
        cond2  =  cluster["Y"] <=  ymean
        subclstr = cluster.loc[ cond1 & cond2 , ]
        State.append([State[indx][0]+NewStep,State[indx][1],NewStep, subclstr.shape[0] ])
         
        cond1  =  cluster["X"] >  xmean 
        cond2  =  cluster["Y"] >  ymean
        subclstr = cluster.loc[ cond1 & cond2 , ]
        State.append([State[indx][0]+NewStep,State[indx][1]+NewStep,NewStep, subclstr.shape[0] ])
        
        State.remove(State[indx])
         
        maxden = np.max( [ State[i][3] for i in range(len(State)) ] ) 
#        print(maxden,len(State))
         
    return State   

#[State[i]   for i in range(len(State)) if State[i][2]>1 ]
#######################################################################
    

if __name__ == "__main__":  
        
    start_time = time.time() 
    ct = pd.read_csv("cities.csv")
    #ct = ct.head(5000)
    density = 300
    N = ct.shape[0]
    sqrtn = math.sqrt(N)
    
    
    ct["X"] = ct["X"] - ct["X"].min()
    ct["Y"] = ct["Y"] - ct["Y"].min()   
    World_X = ct["X"].max() + 0.0001
    World_Y = ct["Y"].max() + 0.0001
    
    bag_area_std =   World_X * World_Y * density / N
    length_std = math.ceil(math.sqrt(bag_area_std) )
    k_x = int(math.ceil(World_X/length_std))
    k_y = int(math.ceil(World_Y/length_std))
    
    
       #State [x,y,step_size,density]
    State  = [[i,j,1,0] for i in range(k_x) for j in range(k_y)]
     
    for i in range(len(State)):  
        cond1a =  ct["X"] >= State[i][0] * length_std
        cond1b =  ct["X"] < (State[i][0]+ State[i][2]) *length_std
        cond2a =  ct["Y"] >= State[i][1] * length_std
        cond2b =  ct["Y"] < (State[i][1] + State[i][2]) * length_std
        cluster = ct.loc[ (cond1a & cond1b) & (cond2a & cond2b ) , ] 
        State[i][3] = cluster.shape[0]
    
    State = fixlowdensity(ct,State,density) 
    State = fixlargedensity(ct,State,density)      
    
     
    outdir = './clusters'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for i in range(len(State)):  
        cond1a =  ct["X"] >= State[i][0] * length_std
        cond1b =  ct["X"] <= (State[i][0]+ State[i][2]) *length_std
        cond2a =  ct["Y"] >= State[i][1] * length_std
        cond2b =  ct["Y"] <= (State[i][1] + State[i][2]) * length_std
        cluster = ct.loc[ (cond1a & cond1b) & (cond2a & cond2b ) , ] 
        filename = 'c_'+str(i).zfill(4)+'_'+str(State[i][0])+'_'+str(State[i][1]) +'.csv'
        fullname = os.path.join(outdir, filename)    
         
        cluster.to_csv(fullname,index=False)
     
  
### now anchors for States
        
             
    tot=0
    outdir = './clusters' 
    state_anchors = []
    for i in range(N):  
        filename = 'c_'+str(i).zfill(4)+'_'+str(State[i][0])+'_'+str(State[i][1]) +'.csv'
        fullname = os.path.join(outdir, filename)    
        
        state = pd.read_csv(fullname, index_col=None) 
        
        xmean = np.mean(state["X"]) 
        ymean = np.mean(state["Y"])
        state_anchors.append([i,xmean,ymean])
        tot+= state.shape[0]
        
        
         
    outdir = './clusterWorld'
    filename = 'state_anchors.csv' 
    fullname = os.path.join(outdir, filename)  
    file = open(fullname, 'a+', newline ='') 
    with file:     
        write = csv.writer(file)  
        write.writerows(state_anchors)  
 