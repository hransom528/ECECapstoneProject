# Quick Setup Guide for Motor HAT:
# Update and install dependencies:
#    sudo apt update && sudo apt install python3-pip python3-smbus i2c-tools -y
# Enable I2C:
#    sudo raspi-config  -> Interfacing Options -> Enable I2C
# Install Adafruit Blinka & MotorKit:
#    pip3 install adafruit-blinka adafruit-circuitpython-motorkit
# Run this script

import time
import board
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

print("Running Motors")

kit.motor1.throttle = 1
kit.motor3.throttle = 1

try:
	while True:
		time.sleep(1)
except KeyboardInterrupt:
	print("Stopping Motors")
	kit.motor1.throttle = 0
	kit.motor3.throttle = 0
	print ("Test Complete")
