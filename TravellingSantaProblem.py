# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 17:58:04 2021

@author: HamidMo
"""


import pandas as pd
import csv,os,sys,time
from MST import MinSpanningTree, AppendMatching, FindEulerianTour
from TSPtools import   ComputeDistMatrix

if __name__ == "__main__":  
    if(len(sys.argv)<2):
        print("Enter input culster names as argv")
        exit() 
     
    inputfile = str(sys.argv[1])	
    
    #inputfile = "clusters/c_0037_10_20.csv"
    
    start_time = time.time() 
    
    ct = pd.read_csv(inputfile) 
    
    dist_matrix = pd.DataFrame(columns=['u','v', 'dist_uv'] ) 
    dist_matrix.astype(dtype= {"u":"int", "v":"int","dist_uv":"double"})
    dist_matrix = ComputeDistMatrix(ct) 
    
    TSP=[]
    if (ct.shape[0]==0):
        TSP=[]
    elif (ct.shape[0]==1):
        TSP = [ ct["CityId"][0] ]
    else: 
        mst = MinSpanningTree(ct,dist_matrix)
        HyperGraph = AppendMatching(ct,mst,dist_matrix)
        TSP = FindEulerianTour(HyperGraph)
     
        
    # writing the data into the file 
    outdir = './clusterTSP'
    filename = 's'+str(sys.argv[1])[10:16] +'.csv'
    fullname = os.path.join(outdir, filename)      
    file = open(fullname, 'a+', newline ='') 
    with file:     
        write = csv.writer(file)  
        write.writerows([TSP]) 
    
    
    # outdir = './clusterWorld'
    # filename = 'world_puzzle.csv' 
    # fullname = os.path.join(outdir, filename)  
    # file = open(fullname, 'a+', newline ='') 
    # with file:     
    #     write = csv.writer(file)  
    #     write.writerows(endpoints)  
    
    print("Computation time: %s seconds." % (time.time() - start_time))
