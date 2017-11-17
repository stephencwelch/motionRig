####################################
##
## trajectoryPlanning.py
## Stephen Welch
##
####################################

import numpy as np
import matplotlib.pyplot as plt

class SimpleQuadraticTrajectory(object):
    '''
    Simple quadratic trajectory planner. (should) achieve smooth starts and stops 
    by using quadratic function at the ends, and matching first derivatives. 
    '''
    
    def __init__(self, tu, tt, p1, p2):
        
        self.tu = float(tu) #Ramp-up time
        self.tt = float(tt) #Total Time
        self.td = tt - tu # Ramp-down time, presently I've only implement this when the time to 
                          # ramp up equals the time to ramp down!

        self.p1 = float(p1) # starting position, ticks
        self.p2 = float(p2) # ending position, ticks
        
        #Compute linear and quadratic coefficients!
        self.a = (self.p1-self.p2)/(2*(self.tu**2-self.tu*self.tt))
        self.e = -1*self.a
        self.c = 2*self.a*self.tu
        self.b = self.p1
        self.f = self.p2
        self.d = (self.p1+self.p2-self.c*self.tt)/2
        
    def compute(self, t):
        if t < self.tu:
            return self.a*t**2+self.b

        elif t>=self.tu and t<=self.td:
            return self.c*t+self.d 

        elif t > self.td:
            return self.e*(self.tt-t)**2+self.f
    
    def visualize(self):
        times = np.linspace(0, self.tt, 100)
        trajectory = []

        for tim in times:
            trajectory.append(self.compute(tim))
            
        plt.plot(times, trajectory)
        plt.grid(1)   