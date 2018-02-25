''' 
Dominion Markov
Author: Tristan Miller
This contains code to read data from the SQL database, and put it in figures
'''
#import pandas as pd
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
#import scipy
#import sklearn
import time
#import sys
#import re
import sqlite3 as lite

#Note: SQL has the following tables
'''sim_types(id integer primary key,
            name text,
            p0_name text,
            p1_name text,
            p2_name text,
            p3_name text,
            p4_name text,
            card_types integer,
            unique(name))
  sim_results(id integer primary key,
            sim_type_id integer,
            sim_version integer,
            p0 real,
            p1 real,
            p2 real,
            p3 real,
            p4 real,
            stdev real,
            mean real,
            reliability real,
            deleted bit)'''

#I'm only making a few figures, so these are pretty much ad hoc functions
def lab_sim_fig():
    #get data from database
    con = lite.connect('sim.db')
    with con:
        cur = con.cursor()        
        cmd = '''select mean,stdev,reliability,p1
            from sim_results
            where sim_type_id = 5
            and deleted = 0
            and p0 = 2000'''
        cur.execute(cmd)
        
        results = cur.fetchall()
    con.close()
    
    #Process the results
    num_results = len(results)
    L = np.zeros(num_results)
    mean = np.zeros(num_results)
    mean_dud = np.zeros(num_results)
    stdev = np.zeros(num_results)
    reliability = np.zeros(num_results)

    for i in range(num_results):
        L[i] = results[i][3]
        reliability[i] = results[i][2]
        mean[i] = results[i][0]*(1-reliability[i]) + 2000*reliability[i]
        mean_dud[i] = results[i][0]
        stdev[i] = ((results[i][1]**2 + results[i][0]**2)*(1-reliability[i]) + 2000**2*reliability[i] - mean[i]**2 )**0.5
        #stdev[i] = results[i][1]
        
    sorter = np.argsort(L)
    L = L[sorter]
    mean = mean[sorter]
    mean_dud = mean_dud[sorter]
    stdev = stdev[sorter]
    reliability = reliability[sorter]
    
    sub_i = L < 0.5
    super_i = L >= 0.5
    
    x_sub = L[sub_i]
    y_sub = mean[sub_i]
    x_super = L[super_i]
    reliability = reliability[super_i]
    #Not plotting stdev or mean_dud, although I could
    #stdev_sub = stdev[sub_i]

    #plot mean and standard deviation in subcritical phase
    plt.plot(x_sub,y_sub,color='#bb8844',lw=2)
    #plt.fill_between(x_sub,y_sub+stdev_sub,y_sub-stdev_sub,color='#ddaa44',alpha=0.25)
    plt.axis([0, 1, 0, 40])
    plt.xlabel('Fraction Labs',fontsize=16)
    plt.tick_params(labelsize=16)
    plt.ylabel('Expected Payoff',color='#bb8844',fontsize=16)
    plt.tick_params(labelsize=16)

    #draw line at phase transition
    l = plt.axvline(x=0.5, color='#000000',lw=2,linestyle='dashed')

    #plot reliability in supercritical phase
    ax2 = plt.gca().twinx()
    ax2.plot(x_super, reliability, 'b',lw=2)
    plt.axis([0, 1, 0, 1])
    plt.ylabel('Reliability', color='b',fontsize=16)
    plt.tick_params(labelsize=16)
    plt.title('Laboratory Engine',fontsize=24)
    
def lab_fin_fig():
    #get data from database
    con = lite.connect('sim.db')
    with con:
        cur = con.cursor()        
        cmd = '''select mean,stdev,p0,p1
            from sim_results
            where sim_type_id = 6
            and deleted = 0
            and p0 = 15 + p1'''
        cur.execute(cmd)
        
        results = cur.fetchall()
    con.close()
    
    #Process the results
    num_results = len(results)
    L = np.zeros(num_results)
    mean = np.zeros(num_results)
    stdev = np.zeros(num_results)

    for i in range(num_results):
        L[i] = results[i][3]/(results[i][2])
        mean[i] = results[i][0]
        stdev[i] = results[i][1]
        
    sorter = np.argsort(L)
    L = L[sorter]
    mean = mean[sorter]
    stdev = stdev[sorter]

    #plot mean and standard deviation in subcritical phase
    plt.plot(L,mean,color='#bb8844',lw=2)
    plt.fill_between(L,mean+stdev,mean-stdev,color='#ddaa44',alpha=0.25)
    plt.axis([0, .8, 0, 20])
    plt.xlabel('Fraction Labs',fontsize=16)
    plt.tick_params(labelsize=16)
    plt.ylabel('Expected Payoff',color='#bb8844',fontsize=16)
    plt.tick_params(labelsize=16)

    #draw line at phase transition
    l = plt.axvline(x=0.4, color='#000000',lw=2,linestyle='dashed')
    
    plt.title('Lab deck with 15 Copper',fontsize=24)
    
def vsm_sim_fig():
    #Initialize arrays
    density = 100
    mean = np.zeros((density,density))
    mean_dud = np.zeros((density,density))
    stdev = np.zeros((density,density))
    reliability = np.zeros((density,density))
    mean[:] = np.nan
    mean_dud[:] = np.nan
    stdev[:] = np.nan
    reliability[:] = np.nan
    
    i,j = np.indices((density,density))
    V_coord = i/density
    S_coord = j/density
    
    #get data from database
    con = lite.connect('sim.db')
    with con:
        cur = con.cursor()
        for i,j in np.ndindex((density,density)):
            
            cmd = '''select avg(mean),avg(reliability),avg(stdev),avg(p0)
                from sim_results
                where sim_type_id = 7
                and deleted = 0
                and p0 >= 1000
                and p2 >= %.3f and p2 < %.3f
                and p3 >= %.3f and p3 < %.3f''' % (i/density,(i+1)/density,j/density,(j+1)/density)
            cur.execute(cmd)
            results = cur.fetchone()
            
            if results[0] is not None:
                reliability[i,j] = results[1]
                mean[i,j] = results[0]*(1-results[1]) + results[3]*results[1]
                mean_dud[i,j] = results[0]
                stdev[i,j] = results[2]
            
    con.close()
    
    #Separate out the subcritical and supercritical parts
    sub_mean = mean
    sub_mean[np.logical_and(V_coord > .25,V_coord > 1-S_coord*3)] = np.nan
    reliability[np.logical_or(V_coord < .25, V_coord < 1-S_coord*3)] = np.nan
    
    critical_S = np.array([0,.25,.75])
    critical_V = np.array([1,.25,.25])
    fig, ax = plt.subplots(figsize=(20,10))
    ax.plot(critical_S,critical_V,lw=3,linestyle="dashed",color='w')
    
    c1 = ax.imshow(sub_mean,extent=(0,1,0,1),origin='lower',interpolation='none',cmap=plt.cm.plasma_r)
    c2 = ax.imshow(reliability,extent=(0,1,0,1),origin='lower',interpolation='none',cmap=plt.cm.winter_r)
    #c1 = plt.contourf(S_coord,V_coord,sub_mean,np.arange(0,10,.2),cmap=plt.cm.plasma_r,extend="both")
    #c2 = plt.contourf(S_coord,V_coord,reliability,10,cmap=plt.cm.GnBu_r)
    ax.set_xlabel('Fraction Smithies',fontsize=24)
    ax.set_ylabel('Fraction Villages',fontsize=24)
    ax.tick_params(labelsize=16)
    
    #c1.cmap.set_under('#EFF821')
    #c1.cmap.set_over('#0C0786')
    c1.set_clim(4, 10)
    
    cax1 = fig.add_axes([0.75, 0.13, 0.03, 0.35]) 
    cbar1 = fig.colorbar(c1,cax = cax1)
    cbar1.ax.set_ylabel('Expected Payoff',fontsize=24)
    cbar1.ax.tick_params(labelsize=16)
    cax2 = fig.add_axes([0.75, 0.53, 0.03, 0.35])
    cbar2 = fig.colorbar(c2,cax = cax2)
    cbar2.ax.set_ylabel('Reliability',fontsize=24)
    cbar2.ax.tick_params(labelsize=16)
    
    ax.set_title('Village/Smithy Engine',fontsize=36)

