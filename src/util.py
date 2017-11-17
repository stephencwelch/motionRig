import numpy as np
import cPickle as pickle 
import roboclaw
import time
import cPickle as pickle
import os.path
import matplotlib.pyplot as plt
from motorControl import *
from trajectoryPlanning import *

def levelRig(motors, home, rc, moveTime = 5.0):

    '''
    Level the motion rig, using home coordatates to determin what level is. 
    '''
    delta = abs(getPositions(motors)[0]-home[0]) - abs(getPositions(motors)[1]-home[1])

    if abs(delta) > 100:
        print 'Rig is not level!, difference from home = ' + str(delta)

        leveledPositions = np.copy(getPositions(motors))
        leveledPositions[0] = leveledPositions[0] + int(round(delta/2))
        leveledPositions[1] = leveledPositions[1] + int(round(delta/2))

    totalTime = moveTime
    rampTime = moveTime/5.0

    startingPositions = getPositions(motors)
    lookAheadTime = 1.0
    tolerance = 50.0 #Anything less than this many ticks we're calling "Not a move"

    motorsToMove = []
    targetPositionsToMove = []
    for i, motor in enumerate(motors):
        if abs(motor.getPosition()-leveledPositions[i]) > tolerance:
            motorsToMove.append(motor)
            targetPositionsToMove.append(leveledPositions[i])

    trajectories = []
    for i, motor in enumerate(motorsToMove):
        trajectories.append(SimpleQuadraticTrajectory(tu = rampTime, tt = totalTime, \
                                                p1 = motor.getPosition(), p2 = targetPositionsToMove[i]))

    for motor in motorsToMove:
        motor.initialize(targetVelocityMin = -2500.0, targetVelocityMax = 2500.0)
        motor.clearTracking()

    startTime = time.time()
    timeElapsed = 0.0

    while timeElapsed < totalTime:
        timeElapsed = time.time()-startTime

        for i, motor in enumerate(motorsToMove):
            lookAheadValue = trajectories[i].compute(timeElapsed + lookAheadTime)
            motor.controlledMove(targetPosition = lookAheadValue, timeToReach = lookAheadTime)

    stopAll(rc)
    savePositions(motors)

    currentDifference = getPositions(motors)[0]-getPositions(motors)[1]
    delta = abs(getPositions(motors)[0]-home[0]) - abs(getPositions(motors)[1]-home[1])
    print 'Rig Leveled! Difference from home = ' + str(delta)
