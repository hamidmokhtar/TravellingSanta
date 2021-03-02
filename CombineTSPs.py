#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 16:21:58 2021

@author: hamid
"""

import pandas as pd
import os,csv
from TSPtools import isprime,distance_uv , calcCircuitCost


def ReorderCities(start,step,cities_s,City_dict):
    K = len(cities_s)
    dist = 100000000.0
    ini_ind =0
    X = City_dict["X"][start], City_dict["Y"][start]
    pr=isprime(City_dict["CityId"][start])
    tnth= start % 10 == 0
    for t in range(K):
        Y= City_dict["X"][cities_s[t]], City_dict["Y"][cities_s[t]]   
        d = distance_uv(X,Y, pr , tnth )
        if d < dist :
            d=dist
            ini_ind = t
    
    return cities_s[ini_ind:]+cities_s[:ini_ind]



if __name__ == "__main__":  
        
    inputfile = "cities.csv" 
    ct = pd.read_csv(inputfile)  
    ct["IsPrime"] = ct.apply(lambda c: isprime(c["CityId"]) , axis=1 ) 
    City_dict = ct.to_dict()
    
       
    inputfile = "clusterTSP/StateRoad.csv"
    StaAnc =  pd.read_csv(inputfile,header=None)
    N = StaAnc.shape[1]
    stateroad = [ StaAnc[i][0]  for i in range(N)]
    
    
    outdir = './clusterTSP'
    SantaTSP=[]
    for state_ind in range(N):
         
        state = stateroad[state_ind]
        filename="s_"+str(state).zfill(4)+"_.csv"  
        fullname = os.path.join(outdir, filename)   
        
        try:
           cities_s =  pd.read_csv(fullname,header=None)     
        except:
           print("this file does not exist:", filename)
           continue 
       
        cities_s = [ cities_s[i][0]  for i in range(cities_s.shape[1])]
         
        #finding closest city from the next state to current city
        if len(SantaTSP)>0 :
           cities_s = ReorderCities(SantaTSP[-1],len(SantaTSP)-1,cities_s,City_dict)
            
        SantaTSP = SantaTSP + cities_s
        #endfor
        
    
    #fixing TSP for repeated cities (issue raised when clustering was not disjoint),no time to fix now
    ####
    for i in range(0,len(SantaTSP)):
        if SantaTSP[i]==0: 
            zro = i
            break    
    SantaTSP = SantaTSP[zro:] + SantaTSP[:zro]   
    Unq_SantaTSP = [SantaTSP[0]]
    for i in range(1,len(SantaTSP)):
        if SantaTSP[i] not in  Unq_SantaTSP:
            Unq_SantaTSP.append(SantaTSP[i]) 
    SantaTSP=Unq_SantaTSP
    ####
    
    
    outdir = './clusterTSP'
    filename = '_SantaCircuitPath_____.csv'
    fullname = os.path.join(outdir, filename)  
     
    file = open(fullname, 'a+', newline ='') 
    with file:     
        write = csv.writer(file)  
        write.writerows([SantaTSP]) 
    
    
    TotalTSPCost = calcCircuitCost(SantaTSP,City_dict)
    print("The Cost of this Santa path is ", TotalTSPCost)
  