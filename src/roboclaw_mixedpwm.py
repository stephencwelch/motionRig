import time
import roboclaw

#Windows comport name
roboclaw.Open("COM3",115200)
#Linux comport name
#roboclaw.Open("/dev/ttyACM0",115200)

address = 0x80

roboclaw.ForwardMixed(address, 0)
roboclaw.TurnRightMixed(address, 0)

while(1):
	roboclaw.ForwardMixed(address, 64)
	time.sleep(2)
	roboclaw.BackwardMixed(address, 64)
	time.sleep(2)
	roboclaw.TurnRightMixed(address, 64)
	time.sleep(2)
	roboclaw.TurnLeftMixed(address, 64)
	time.sleep(2)
	roboclaw.ForwardMixed(address, 0)
	roboclaw.TurnRightMixed(address, 64)
	time.sleep(2)
	roboclaw.TurnLeftMixed(address, 64)
	time.sleep(2)
	roboclaw.TurnRightMixed(address, 0)
	time.sleep(2)
