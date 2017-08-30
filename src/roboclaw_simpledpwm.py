import time
import roboclaw

#Windows comport name
roboclaw.Open("COM3",115200)
#Linux comport name
#roboclaw.Open("/dev/ttyACM0",115200)

address = 0x80

while(1):
	roboclaw.ForwardM1(address,64)
	roboclaw.BackwardM2(address,64)
	time.sleep(2)
	
	roboclaw.BackwardM1(address,64)
	roboclaw.ForwardM2(address,64)
	time.sleep(2)

	roboclaw.ForwardBackwardM1(address,96)
	roboclaw.ForwardBackwardM2(address,32)
	time.sleep(2)
	
	roboclaw.ForwardBackwardM1(address,32)
	roboclaw.ForwardBackwardM2(address,96)
	time.sleep(2)
