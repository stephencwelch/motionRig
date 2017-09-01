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
import cPickle as pickle
import os.path
import matplotlib.pyplot as plt


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

def getPositions(motors):
    position = []
    for motor in motors:
        position.append(motor.getPosition())
        
    return position

def savePositions(motors):
    for motor in motors:
        motor.savePosition()


class Motor(object):
    '''
        Abstact each motor into a mother-fucking class. 
    '''

    def __init__(self, address, motorNumber, rc, signFlipped = False, motorCounter = 0, kPID = [1.0, 1.0]):
        self.address = address
        self.motorNumber = motorNumber
        self.rc = rc
        self.kPID = kPID
        self.signFlipped = signFlipped
        self.motorCounter = motorCounter

        ## Check for position pickle, if it doesn't exist create one. 
        ## If it does exist, set encoder position to these values:
        self.saveDir = 'logs/' + str(self.motorCounter) + '.p'
        if os.path.isfile(self.saveDir):
            f = open(self.saveDir, 'r')
            savedPosition = pickle.load(f)
            f.close()
            #Set encoders to saved position!
            if self.motorNumber == 1:
                self.rc.SetEncM1(self.address, savedPosition)
            elif self.motorNumber == 2:
                self.rc.SetEncM2(self.address, savedPosition)
        else:
            f = open(self.saveDir, 'wb')
            pickle.dump(self.getPosition(), f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()

        ## Initialize Tracking Information
        self.tracking = {}
        self.tracking['voltages'] = []
        self.tracking['positions'] = []
        self.tracking['timeElapsed'] = []
        self.tracking['targetVelocities'] = []
        self.tracking['velocities'] = []
        self.tracking['targetPosition'] = []
        self.tracking['errors'] = []

    def stop(self):
        if self.motorNumber == 1:
            self.rc.ForwardM1(self.address, 0)
        elif self.motorNumber == 2:
            self.rc.ForwardM2(self.address, 0)
            
    def move(self, voltage, direction):
        '''
            Move motor in specified direction with specified voltage.
        '''
        if self.signFlipped:
            direction = -1*direction
        
        #use sign of velocity to figure out which way to go here:
        if self.motorNumber == 1:
            if direction > 0:
                self.rc.ForwardM1(self.address, voltage)
            else:
                self.rc.BackwardM1(self.address, voltage)
        elif self.motorNumber == 2:
            if direction > 0:
                self.rc.ForwardM2(self.address, voltage)
            else:
                self.rc.BackwardM2(self.address, voltage)

    def getPosition(self):
        '''
        Read encoder position.
        '''
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
        self.tracking['errors'] = []
        
    def restartTimer(self):
        self.startTime = time.time()
    
    def visualizeMove(self):
        fig = plt.figure(0, (10,8))
        plt.subplot(4,1,1)
        plt.plot(self.tracking['timeElapsed'], self.tracking['positions'], 'b')
        plt.plot(self.tracking['timeElapsed'], self.tracking['targetPosition'], 'r')
        plt.legend(['Actual Position', 'Target Position'], loc = 0)
        plt.grid(1)
        plt.title('Positions')

        plt.subplot(4,1,2)
        plt.plot(self.tracking['timeElapsed'], self.tracking['velocities'], 'm-x')
        plt.plot(self.tracking['timeElapsed'], self.tracking['targetVelocities'], 'c-x')
        plt.grid(1)
        plt.legend(['Velocity Est', 'Velocity Target'], loc = 0)
        #plt.ylim([-3500, 3500])

        plt.subplot(4,1,3)
        plt.plot(self.tracking['timeElapsed'], self.tracking['errors'], 'y-x')
        plt.grid(1)
        plt.legend(['Velocity Errors'], loc = 0)

        plt.subplot(4,1,4)
        plt.plot(self.tracking['timeElapsed'], self.tracking['voltages'], 'g-x')
        plt.grid(1)
        plt.title('Voltages')

    def initialize(self, targetVelocityMin = -1000.0, targetVelocityMax = 1000.0):
        self.targetVelocityMin = targetVelocityMin
        self.targetVelocityMax = targetVelocityMax
        self.oldPosition = self.getPosition()
        self.oldTime = time.time()
        self.startTime = time.time()
        self.oldVoltage = 0.0
        self.oldError = 0.0

    def resetEncoders(self):
        self.rc.ResetEncoders(self.address)

    def savePosition(self):
        position = self.getPosition()
        f = open(self.saveDir, 'wb')
        pickle.dump(position, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()

    def controlledMove(self, targetPosition, timeToReach, verbose = False):
        '''
        Move to target position in requested amount of time using simple controls. Use Proportional, 
        and maybe proportional/derivative controls to minimize voltage error. 
        '''

        #How far has the motor moved?
        newPosition = self.getPosition()

        #What time it is?
        newTime = time.time()

        #Compute this sucker's velocity:
        self.velocity = float(newPosition-self.oldPosition)/(newTime-self.oldTime)

        #Only update target velocity if we have some time left:
        if timeToReach > 1e-2:
            self.remainingTime = timeToReach
      
            distToMove = float(targetPosition - newPosition)
            self.targetVelocity = distToMove/self.remainingTime

            #Target Velocity blows up as remainingTime appraoches 0, let's clip:
            if self.targetVelocity > self.targetVelocityMax:
                self.targetVelocity = self.targetVelocityMax

            elif self.targetVelocity < self.targetVelocityMin:
                self.targetVelocity = self.targetVelocityMin
            
            #Compute velocity error
            newError = self.targetVelocity - self.velocity

            #Update Voltage
            newVoltage = self.oldVoltage + self.kPID[0]*newError
            
            #Check to make sure new voltage is between 0 and 127:
            if newVoltage > 127:
                newVoltage = 127
                print 'excess voltage on motor ' + str(self.motorCounter)
            elif newVoltage < -127:
                newVoltage = -127
                print 'voltage too low on motor ' + str(self.motorCounter)

            #And actually turn motors!
            self.move(int(round(abs(newVoltage))), np.sign(newVoltage))

            #Update xtv
            self.oldVoltage = newVoltage
            self.oldPosition = newPosition
            self.oldTime  = newTime
            self.oldError = newError
        
            #Update tracking information
            self.tracking['voltages'].append(newVoltage)
            self.tracking['positions'].append(newPosition)
            self.tracking['timeElapsed'].append(time.time()-self.startTime)
            self.tracking['targetVelocities'].append(self.targetVelocity)
            self.tracking['velocities'].append(self.velocity)
            self.tracking['targetPosition'].append(targetPosition)
            self.tracking['errors'].append(newError)

            if verbose:
                print 'Voltage = {}'.format(newVoltage)
        

