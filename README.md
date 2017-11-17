# motionRig

A set of python tools for controlling a Welch Labs motion rig. If you have a Welch Labs motion rig, and your name isn't Stephen Welch, I have no idea how you got one. Perhaps you stole it. If you did steal it, 1) that's amazing, that thing is really hard to move, 2) please return it. 

# About this Repository
This repository contains a set of methods designed to control a 5-axis motion rig. I'm seeking here to create something that I can quickly use to get the shots I want. 

# Relative and Absolute Positioning
A hard-reset can destroy my absolute positioning. For this reason, I'm introducing the following convention: one absolute home position, and all other saved positions are defined relative to this home position. This way, assuming I don't do any 
motor swaps to motors with different RPMs, if I lose absolute home it will only take one recalibration to get all my old positions back. For now I'll do this inside notebooks, and later bake it into my classes, or create a new class. 

## To Do
- Positional Memory on emergency stop.
- Put absolute and relative position saving in classes. 
- Smooth Motion Through multiple waypoints
- Figure out how to program a "keep looking at the same spot" mode - where I can move the u/d l/r f/b axes, and the pan tilt controllers do thier best to remain focused on a single point.

# Complete (ish)
- Wrap up my motor class and possible some other stuff into nice importable scripts.
- Create a couple ipython notebook example cases
- Write a "persistent memory" for my motor class - this will be super helpful!


