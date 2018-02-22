''' 
Dominion Markov
Author: Tristan Miller
This contains code for Monte Carlo and Markov Chain simulations
'''
#import pandas as pd
import numpy as np
from numpy import random
#import matplotlib.pyplot as plt
#import scipy
#import sklearn
import time
#import sys
#import re
import sqlite3 as lite

#######################################
############ SQL Database  ############
#######################################

#This will initialize the SQL database.  Meant to be run only once.
def init_sql_database():
    con = lite.connect('sim.db')
    with con:
        cur = con.cursor()
        #First create a table for each kind of sim, e.g. monte carlo sim for a finite lab/copper deck
        #since different sims will have different kinds of parameters, their names will be provided here.
        #card_types is the number of kinds of cards in the sim, e.g. 2 for lab/copper
        sqlcmd = '''
        create table sim_types( 
            id integer primary key,
            name text,
            p0_name text,
            p1_name text,
            p2_name text,
            p3_name text,
            p4_name text,
            card_types integer,
            unique(name))'''
        cur.execute(sqlcmd)
        
        #Next create a table with rows for the results of each simulation
        #deleted is 1 if I want to get rid of the row
        #sim_version is the version of the simulation being used.  This makes it easier to delete outdated results
        sqlcmd = '''
        create table sim_results(
            id integer primary key,
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
        cur.execute(sqlcmd)
    con.close()

#######################################
######## Abstract dom_sim class #######
#######################################

#Each kind of simulator will be its own class, each inheriting dom_sim.
#It turns out I don't need to include much here, but I outline and describe the functions I want in each class.
class dom_sim:
    #sim_type = "<etc.>" #Name of the simulation type
    #card_types = <#> #Number of card types
    #parameter_names = [<max_cards/deck_size>,<etc.>] #Parameters used to define simulation (up to 5 allowed)
    #is_finite = <True/False>
    #version = <#> 
    
    #def __init__(self,<etc.>):
    
    #initializes the p_vector, which describes the composition of the remaining deck
    #def init_p_vector(self):
    
    #Draws a single card.
    #def draw(self):
    
    #Plays a single action.  success is false if this fails
    #def action(self):
    #    return success
    
    #Runs a simulation of a single turn.
    #def turn(self):
    #    return payoff
    
    #Runs the simulation (possibly simulating many turns) and returns statistics, which are written to the database
    #mean and stdev are statistics only on turns with *finite* payoff, and reliability is the probability of infinite payoff
    #def sim(self):
        #self.write_to_sql(mean,stdev,reliability)
        #return (mean,stdev,reliability)
    
    #Writes the results to the database
    def write_to_sql(self,mean,stdev,reliability):
        con = lite.connect('sim.db')
        with con:
            cur = con.cursor()
            #If this simulation type isn't already in the database, add it.
            sqlcmd = '''
            insert or ignore into sim_types(name, {parameter_string}card_types)
                values("{name}", {parameter_names}{card_types})'''
            ps_string = ''
            pn_string = ''
            for i in range(len(self.parameters)):
                ps_string += 'p' + str(i) + '_name, '
                pn_string += '"' + self.parameter_names[i] + '", '
            sqlcmd = sqlcmd.format(parameter_string=ps_string, name=self.sim_type, parameter_names = pn_string, card_types=self.card_types)
            cur.execute(sqlcmd)
            
            #Insert the results of the simulation
            sqlcmd = '''
            insert into sim_results(sim_type_id, sim_version,{parameters}stdev, mean, reliability, deleted)
                values((select id from sim_types where name = "{name}"), {version}, 
                {parameter_values}{stdev}, {mean}, {reliability}, 0)'''
            p_string = ''
            pv_string = ''
            for i in range(len(self.parameters)):
                p_string += "p" + str(i) + ", "
                pv_string += str(self.parameters[i]) + ", "
            sqlcmd = sqlcmd.format(version=self.version,parameters=p_string, name=self.sim_type, parameter_values=pv_string, stdev=stdev, mean=mean, reliability=reliability)
            #print(sqlcmd)
            cur.execute(sqlcmd)
        con.close()


#######################################
####### Monte Carlo simulations #######
#######################################

#This is the abstract class of sims that use a monte carlo method
class monte_sim(dom_sim):        
    #sim_type = "Monte <etc.>"
    #card_types = <#>
    #parameter_names = [<max_cards/deck_size>,"stat_weight",<etc.>]
    #is_finite = <True/False>
    #version = <#>
    
    #def __init__(self,<parameters>):
        #check if parameters are right types
    #    self.parameters = <etc.>
    #    self.monte_init()
    
    #Initializes parameters for the start of turn.  Should be the same in all monte carlo sims.
    def monte_init(self):
        self.cards_drawn = 0 #cards drawn so far
        self.action_supply = 1 #remaining action supply
        self.card_vector = [0]*self.card_types #The number of each type of card in hand.  *The first item is copper by default.*
        self.init_p_vector() #numbers characterizing the composition of the remaining deck.
        
    #initializes the p_vector
    #def init_p_vector(self):
    
    #This draws a single card.  By default, this assumes an infinite deck.
    def draw(self):
        rn = random.rand()
        for i in range(self.card_types-1):
            if rn < self.p_vector[i]:
                i -= 1
                break
            else:
                rn -= self.p_vector[i]
        i += 1
        self.card_vector[i] += 1
        self.cards_drawn += 1
    
    #Plays a single action.  success is false if this fails
    #def action(self):
    #    return success
    
    #Draws 5 cards, and then plays actions until unable or reach maximum number of cards
    def turn(self):
        self.monte_init()
        for i in range(5):
            self.draw()

        action_check = True
        max_cards = self.parameters[0] #for finite simulations this condition is irrelevant
        while(action_check and (self.cards_drawn < max_cards)):
            action_check = self.action()

        if action_check and not self.is_finite:
            return np.inf
        else:
            return self.card_vector[0] #here we assume the first item of card_vector is copper
    
    #Runs the simulation multiple times and collects statistics
    def sim(self):
        running_count = 0
        running_sum = 0
        running_sqsum = 0
        num_sims = self.parameters[1]
        for i in range(num_sims):
            payoff = self.turn()
            if np.isfinite(payoff):
                running_count += 1
                running_sum += payoff
                running_sqsum += payoff**2

        reliability = 1 - running_count/num_sims
        if running_count > 0:
            mean = running_sum / running_count
            stdev = (running_sqsum / running_count - mean**2)**0.5
            self.write_to_sql(mean,stdev,reliability)
            return(mean,stdev,reliability)
        else:
            self.write_to_sql(0,0,reliability)
            return(np.nan,np.nan,reliability)

#A monte carlo sim for an infinite lab_copper deck.
class monte_lab_inf(monte_sim):
    
    sim_type = "Monte Lab Infinite"
    card_types = 2
    parameter_names = ["max_cards","stat_weight","fraction_labs"]
    is_finite = False
    version = 1
    
    def __init__(self,fraction_labs,max_cards=1000,num_sims=1000):
        if fraction_labs > 1:
            raise ValueError("Error: expected fraction of labs less than 1")
            return
        self.parameters = [max_cards,num_sims,fraction_labs]
        self.monte_init()
    
    #p_vector is the fraction of coppers in deck
    def init_p_vector(self):
        self.p_vector = [1-self.parameters[2]]
    
    #Plays a lab if able
    def action(self):
        if self.card_vector[1] >= 1:
            self.card_vector[1] -= 1
            self.draw()
            self.draw()
            return True
        else:
            return False

#A monte carlo sim for a finite lab/copper deck
class monte_lab_fin(monte_lab_inf):
    
    sim_type = "Monte Lab Finite"
    parameter_names = ["deck_size","stat_weight","num_labs"]
    is_finite = True
    version = 1
    
    def __init__(self,num_labs,deck_size=30,num_sims=1000):
        if not isinstance(num_labs,int):
            raise ValueError("Error: expected integer number of labs")
            return
        self.parameters = [deck_size,num_sims,num_labs]
        self.monte_init()
    
    #Here, the p_vector is the number of cards of each type remaining in the deck.
    def init_p_vector(self):
        self.p_vector = [self.parameters[0]-self.parameters[2],self.parameters[2]]
    
    #This function must be overridden, because p_vector is a different format
    def draw(self):
        cards_left = sum(self.p_vector)
        if cards_left == 0:
            #draw fails because deck is empty
            return
        rn = random.rand()*cards_left
        for i in range(self.card_types-1):
            if rn < self.p_vector[i]:
                i -= 1
                break
            else:
                rn -= self.p_vector[i]
        i += 1
        self.card_vector[i] += 1
        self.p_vector[i] -= 1
    
#A monte carlo sim for an infinite village/smithy deck.
class monte_vsm_inf(monte_sim):
    
    sim_type = "Monte Village/Smithy Infinite"
    card_types = 3
    parameter_names = ["max_cards","stat_weight","fraction_villages","fraction_smithies"]
    is_finite = False
    version = 1
        
    def __init__(self,fraction_villages,fraction_smithies,max_cards=1000,num_sims=1000):
        if fraction_villages + fraction_smithies > 1:
            raise ValueError("Error: expected fraction of action cards less than 1")
            return
        self.parameters = [max_cards,num_sims,fraction_villages,fraction_smithies]
        self.monte_init()
        
    #p_vector is the fraction of [coppers,villages] in deck
    def init_p_vector(self):
        self.p_vector = [1-self.parameters[2]-self.parameters[3],self.parameters[2]]
        
    #Plays a village if able, otherwise a smithy
    def action(self):
        if self.action_supply == 0:
            #If there are no actions left, this fails
            return False
        elif self.card_vector[1] >= 1:
            #play a village
            self.card_vector[1] -= 1
            self.draw()
            self.action_supply += 1
            return True
        elif self.card_vector[2] >= 1:
            #play a smithy
            self.card_vector[2] -= 1
            self.draw()
            self.draw()
            self.draw()
            self.action_supply -= 1
            return True
        else:
            #if no cards to play, this fails
            return False
    
#Just for fun, here's a sim of a Herald deck
class monte_herald_inf(monte_sim):
    
    sim_type = "Monte Herald Infinite"
    card_types = 2
    parameter_names = ["max_cards","stat_weight","fraction_heralds"]
    is_finite = False
    version = 1
        
    def __init__(self,fraction_heralds,max_cards=1000,num_sims=1000):
        if fraction_heralds > 1:
            raise ValueError("Error: expected fraction of heralds less than 1")
            return
        self.parameters = [max_cards,num_sims,fraction_heralds]
        self.monte_init()
        
    #p_vector is [fraction_coppers,top_card]
    def init_p_vector(self):
        self.p_vector = [1-self.parameters[2],0]
        self.p_vector[self.card_types-1] = self.check_top()
        
    #Randomizes the identity of the card on top
    def check_top(self):
        rn = random.rand()
        for i in range(self.card_types-1):
            if rn < self.p_vector[i]:
                i -= 1
                break
            else:
                rn -= self.p_vector[i]
        i += 1
        return i
    
    #Draws the top card, and checks top
    def draw(self):
        self.card_vector[self.p_vector[self.card_types-1]] += 1
        self.p_vector[self.card_types-1] = self.check_top()
        self.cards_drawn += 1
        
    #Plays a herald if able
    def action(self):
        if self.card_vector[1] >= 1:
            self.card_vector[1] -= 1
            self.draw()
            if self.p_vector[self.card_types-1] == 1:
                #If top card is a herald, draw again
                self.draw()
            return True
        else:
            return False
        
#######################################
####### Markov Chain simulations ######
#######################################

#This is the abstract class of sims that use a markov chain method

#To do:
#change state_vector and payoff_vector to numpy vectors
#write draw(), turn() and sim()
class markov_sim(dom_sim):        
    #sim_type = "Markov <etc.>"
    #card_types = <#>
    #parameter_names = [<max_cards/deck_size>,<etc.>]
    #is_finite = <True/False>
    #version = <#>
    
    #def __init__(self,<parameters>):
        #check if parameters are right types
    #    self.parameters = <etc.>
    #    self.markov_init()
    
    #Initializes parameters for the start of turn.
    def markov_init(self):
        self.hand_size = 0 #number of cards in hand.  Can be used e.g. to infer coppers in hand.
        self.state_vector = [0]*max_cards #the probability of the game being in any particular state
        #in general, state_vector will be a multi-dimensional matrix.
        #e.g. rows=[number of first action card], columns=[number of 2nd action card], layers=[action supply]
        #but I can't always follow this scheme, since it's so important to reduce the dimensionality.
        
        self.payoff_vector = [0]*max_cards #the probability of getting any particular finite payoff
        self.init_p_vector() #numbers characterizing the composition of the remaining deck.
        
    #initializes the p_vector
    #def init_p_vector(self):
    
    #This draws a single card.  By default, this assumes an infinite deck.
    #def draw(self):
    
    #Plays a single action.  success is false if this fails
    #def action(self):
    #    return success
    
    #Draws 5 cards, and then plays actions until unable or reach maximum number of cards
    #def turn(self):
    
    #Looks at the final state vector
    #def sim(self):