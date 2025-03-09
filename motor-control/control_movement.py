#THIS CODE IS UNTESTED, I HAVE NOT GOTTEN THE CHANCE TO RUN IT ON THE PI YET

import time
import board
import sys
import termios
import tty
from adafruit_motorkit import MotorKit


kit = MotorKit(i2c=board.I2C())

speed = 0.3 

print("Use W/A/S/D to control the motors. Press 'q' to quit.")

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

try:
    while True:
        key = get_key()
        if key == 'w':
            kit.motor1.throttle = speed
            kit.motor3.throttle = speed
            print("Moving forward")
        elif key == 's':
            kit.motor1.throttle = -speed
            kit.motor3.throttle = -speed
            print("Moving backward")
        elif key == 'a':
            kit.motor1.throttle = -speed
            kit.motor3.throttle = speed
            print("Turning left")
        elif key == 'd':
            kit.motor1.throttle = speed
            kit.motor3.throttle = -speed
            print("Turning right")
        elif key == 'q':
            print("Stopping motors and exiting...")
            break
        else:
            kit.motor1.throttle = 0
            kit.motor3.throttle = 0
except KeyboardInterrupt:
    print("Stopping motors...")
finally:
    kit.motor1.throttle = 0
    kit.motor3.throttle = 0
    print("Motor test complete.")
