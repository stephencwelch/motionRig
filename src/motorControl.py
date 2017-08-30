####################################
##
## motorControl.py
## Stephen Welch
##
####################################

import numpy as np
import cPickle as pickle 
import roboclaw
import time

def connect(portName = "/dev/tty.usbserial-A9ETDN3N", baudRate = 115200):
    roboclaw.Open(portName, baudRate)
    return roboclaw

#STOP ALL THE MOTORS (IMPORTANT SHIT)
def stopAll(rc):
    address = 0x80
    rc.ForwardM1(address,0)
    rc.ForwardM2(address,0)
    address = 0x81
    rc.ForwardM1(address,0)
    rc.ForwardM2(address,0)
    address = 0x82
    rc.ForwardM1(address,0)
    rc.ForwardM2(address,0)
    
def manualControl(leftUD=0, rightUD= 0, leftRight=0, fB=0, tilt=0, pan=0):
    '''
    Manually Control Motion Rig.
    '''

    #Up Down Left:
    if leftUD >= 0:
        roboclaw.ForwardM2(0x81, leftUD)
    elif leftUD < 0:
        roboclaw.BackwardM2(0x81, -1*leftUD)

    #Up Down Right:
    if rightUD >= 0:
        roboclaw.ForwardM1(0x81, rightUD)
    elif rightUD < 0:
        roboclaw.BackwardM1(0x81, -1*rightUD)
    
    #Left Right
    if leftRight >= 0:
        roboclaw.ForwardM1(0x80, leftRight)
    elif leftRight < 0:
        roboclaw.BackwardM1(0x80, -1*leftRight)
        
    #forwardBackward
    if fB >= 0:
        roboclaw.ForwardM2(0x80, fB)
    elif fB < 0:
        roboclaw.BackwardM2(0x80, -1*fB)
            
    #tilt
    if tilt >= 0:
        roboclaw.ForwardM1(0x82, tilt)
    elif tilt < 0:
        roboclaw.BackwardM1(0x82, -1*tilt)
        
    #pan
    if pan >= 0:
        roboclaw.ForwardM2(0x82, pan)
    elif pan < 0:
        roboclaw.BackwardM2(0x82, -1*pan)

def getPosition(motors):
    position = []
    for motor in motors:
        position.append(motor.getPosition())
        
    return position

class Motor(object):
    '''
        Abstact each motor into a mother-fucking class. 
    '''

    def __init__(self, address, motorNumber, rc, signFlipped = False, motorCounter = 0, adjustmentIncrement = 5.0):
        self.address = address
        self.motorNumber = motorNumber
        self.rc = rc
        self.adjustmentIncrement = adjustmentIncrement
        self.signFlipped = signFlipped
        self.motorCounter = motorCounter
        
        self.tracking = {}
        self.tracking['voltages'] = []
        self.tracking['positions'] = []
        self.tracking['timeElapsed'] = []
        self.tracking['targetVelocities'] = []
        self.tracking['velocities'] = []

    def stop(self):
        if self.motorNumber == 1:
            self.rc.ForwardM1(self.address,0)
        elif self.motorNumber == 2:
            self.rc.ForwardM2(self.address,0)
            
    def move(self, voltage, direction):
        if self.signFlipped:
            direction = -1*direction
        
        #use sign of velocity to figure out which way to go here:
        if self.motorNumber == 1:
            if direction >0:
                self.rc.ForwardM1(self.address, voltage)
            else:
                self.rc.BackwardM1(self.address, voltage)
        elif self.motorNumber == 2:
            if direction >0:
                self.rc.ForwardM2(self.address, voltage)
            else:
                self.rc.BackwardM2(self.address, voltage)
                
    def getPosition(self):
        if self.motorNumber == 1:
            position = self.rc.ReadEncM1(self.address)[1] 
        elif self.motorNumber == 2:
            position = self.rc.ReadEncM2(self.address)[1] 

        return position
    
    def clearTracking(self):
        self.tracking = {}
        self.tracking['voltages'] = []
        self.tracking['positions'] = []
        self.tracking['timeElapsed'] = []
        self.tracking['targetVelocities'] = []
        self.tracking['velocities'] = []
        self.tracking['targetPosition'] = []
        
    def restartTimer(self):
        self.startTime = time.time()
    
    def visualizeMove(self):
        fig = figure(0, (10,8))
        subplot(3,1,1)
        plot(self.tracking['timeElapsed'], self.tracking['positions'], 'b')
        plot(self.tracking['timeElapsed'], self.tracking['targetPosition'], 'r')
        legend(['Actual Position', 'Target Position'])
        grid(1)
        title('Positions')

        subplot(3,1,2)
        plot(self.tracking['timeElapsed'], self.tracking['velocities'], 'm-x')
        plot(self.tracking['timeElapsed'], self.tracking['targetVelocities'], 'c-x')
        grid(1)
        legend(['Velocity Est', 'Velocity Target'])
        ylim([-3500, 3500])

        subplot(3,1,3)
        plot(self.tracking['timeElapsed'], self.tracking['voltages'], 'g-x')
        grid(1)
        title('Voltages')
        
    def driftToStop(self, decayParam = 0.9):
        if self.oldVoltage != 0:
            newVoltage = decayParam*self.oldVoltage
            
            if newVoltage <= 0:
                newVoltage = 0
                self.velocity = 0
                'reacehed Stop!'

            #And actually turn motors!
            self.move(int(round(newVoltage)), sign(self.targetVelocity))

            self.oldVoltage = newVoltage
            
        else:
            self.velocity = 0
            newVoltage = 0
            self.stop()
            
        #Update tracking information
        self.tracking['voltages'].append(newVoltage)
        self.tracking['positions'].append(self.getPosition())
        self.tracking['timeElapsed'].append(time.time()-self.startTime)
        self.tracking['targetVelocities'].append(self.targetVelocity)
        self.tracking['velocities'].append(self.velocity)
        self.tracking['targetPosition'].append(NaN)
            
    def smoothStart(self, growthParam = 1.01, direction = 1):
        if self.oldVoltage == 0:
            newVoltage = 3
        else:
            newVoltage = growthParam*self.oldVoltage

            if newVoltage >= 128:
                newVoltage = 128
                'maxed out, too much growth!!'

        #And actually turn motors!
        self.move(int(round(newVoltage)), direction)

        #Update xtv
        self.oldVoltage = newVoltage

        #Update tracking information
        self.tracking['voltages'].append(newVoltage)
        self.tracking['positions'].append(self.getPosition())
        self.tracking['timeElapsed'].append(time.time()-startTime)
        self.tracking['targetVelocities'].append(NaN)
        self.tracking['velocities'].append(NaN)
        self.tracking['targetPosition'].append(NaN)
            
    def controlledMove(self, targetPosition, timeToReach, verbose = False):
        #I'll try to make this as simple as I can. 

        #How far has the motor moved?
        if self.motorNumber == 1:
            newPosition = self.rc.ReadEncM1(self.address)[1] 
        elif self.motorNumber == 2:
            newPosition = self.rc.ReadEncM2(self.address)[1] 

        #What time it is?
        newTime = time.time()

        #Compute this sucker's velocity:
        self.velocity = float(newPosition-self.oldPosition)/(newTime-self.oldTime)

        #Target Velocity has likely changed!
        self.remainingTime = timeToReach
        
        #Only recompute if more than 1 second remaining - this guy likes to blow up!
        #SW 8/9 Taking this bit out for now for fancy adaptive control method
        # if timeToReach > 1:
  
        #Below a minium movement threshold, don't try to move. This restuls in controller instability. 
        distToMove = float(targetPosition - newPosition)
        #if abs(distToMove) > 250:
        self.targetVelocity = distToMove/self.remainingTime
        #else:
        #    self.targetVelocity = 0
            
        #Controller Bit:
        error = self.velocity-self.targetVelocity
        
        #This will kick in if We reach target early:
        if abs(self.targetVelocity) != 0:
            percentError = float(abs(error))/self.targetVelocity
        else:
            percentError = 0.1
            
        #knock down huge percent errors:
        if percentError > 1:
            percentError= 1

        if error > 0:
            #Slow Down!
            newVoltage = self.oldVoltage - self.adjustmentIncrement*percentError
        elif error < 0:
            #Speed Up!
            newVoltage = self.oldVoltage + self.adjustmentIncrement*percentError
        elif error ==0:
            newVoltage = self.oldVoltage
            
        #Check to make sure new voltage is between 0 and 128:
        if newVoltage > 128:
            newVoltage = 128
            print 'excess voltage on motor ' + str(self.motorCounter)
        elif newVoltage < 0:
            newVoltage = 0
            print 'voltage too low on motor ' + str(self.motorCounter)

        #And actually turn motors!
        self.move(int(round(newVoltage)), sign(self.targetVelocity))

        #Update xtv
        self.oldVoltage = newVoltage
        self.oldPosition = newPosition
        self.oldTime  = newTime
        
        #Update tracking information
        self.tracking['voltages'].append(newVoltage)
        self.tracking['positions'].append(newPosition)
        self.tracking['timeElapsed'].append(time.time()-startTime)
        self.tracking['targetVelocities'].append(self.targetVelocity)
        self.tracking['velocities'].append(self.velocity)
        self.tracking['targetPosition'].append(targetPosition)

        if verbose:
            print 'Voltage = {}'.format(newVoltage)

