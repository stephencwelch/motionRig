#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
import roboclaw

def displayspeed():
	enc1 = roboclaw.ReadEncM1(address)
	enc2 = roboclaw.ReadEncM2(address)
	speed1 = roboclaw.ReadSpeedM1(address)
	speed2 = roboclaw.ReadSpeedM2(address)

	print("Encoder1:"),
	if(enc1[0]==1):
		print enc1[1],
		print format(enc1[2],'02x'),
	else:
		print "failed",
	print "Encoder2:",
	if(enc2[0]==1):
		print enc2[1],
		print format(enc2[2],'02x'),
	else:
		print "failed " ,
	print "Speed1:",
	if(speed1[0]):
		print speed1[1],
	else:
		print "failed",
	print("Speed2:"),
	if(speed2[0]):
		print speed2[1]
	else:
		print "failed "

#Windows comport name
roboclaw.Open("COM3",38400)
#Linux comport name
#roboclaw.Open("/dev/ttyACM0",115200)

address = 0x80

version = roboclaw.ReadVersion(address)
if version[0]==False:
	print "GETVERSION Failed"
else:
	print repr(version[1])

while(1):
	roboclaw.SpeedAccelDistanceM1(address,12000,12000,42000,1);
	roboclaw.SpeedAccelDistanceM2(address,12000,-12000,42000,1);
	roboclaw.SpeedAccelDistanceM1(address,12000,0,0,0);  #distance travelled is v*v/2a = 12000*12000/2*48000 = 1500
	roboclaw.SpeedAccelDistanceM2(address,12000,0,0,0);  #that makes the total move in one direction 48000
	buffers = (0,0,0)
	while(buffers[1]!=0x80 and buffers[2]!=0x80):	#Loop until distance command has completed
		displayspeed();
		buffers = roboclaw.ReadBuffers(address);
  
	time.sleep(1)

	roboclaw.SpeedAccelDistanceM1(address,48000,-12000,46500,1);
	roboclaw.SpeedAccelDistanceM2(address,48000,12000,46500,1);
	roboclaw.SpeedAccelDistanceM1(address,48000,0,0,0);  #distance travelled is v*v/2a = 12000*12000/2*48000 = 1500
	roboclaw.SpeedAccelDistanceM2(address,48000,0,0,0);  #that makes the total move in one direction 48000
	buffers = (0,0,0)
	while(buffers[1]!=0x80 and buffers[2]!=0x80):	#Loop until distance command has completed
		displayspeed()
		buffers = roboclaw.ReadBuffers(address)
  
	time.sleep(1);  #When no second command is given the motors will automatically slow down to 0 which takes 1 second
