import time
import roboclaw

#Windows comport name
roboclaw.Open("COM3",115200)
#Linux comport name
#roboclaw.Open("/dev/ttyACM0",115200)

while 1:
	#Get version string
	version = roboclaw.ReadVersion(0x80)
	if version[0]==False:
		print "GETVERSION Failed"
	else:
		print repr(version[1])
	time.sleep(1)
