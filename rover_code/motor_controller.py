# Basically the same code as control_movement.py 
# Not sure if the getKey() function is needed

import board
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
speed = 1

def move_forward(speed=1):
    kit.motor1.throttle = -speed
    kit.motor3.throttle = -speed

def move_backward(speed=1):
    kit.motor1.throttle = speed
    kit.motor3.throttle = speed

def turn_left(speed=1):
    kit.motor1.throttle = -speed
    kit.motor3.throttle = speed

def turn_right(speed=1):
    kit.motor1.throttle = speed
    kit.motor3.throttle = -speed

def stop():
    kit.motor1.throttle = 0
    kit.motor3.throttle = 0
