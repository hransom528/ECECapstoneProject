import board
import time
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

def soft_start(motor, target_speed):
    bump = 0.5 * (1 if target_speed > 0 else -1)
    motor.throttle = bump
    time.sleep(0.05)  # small delay to smooth the transition
    motor.throttle = target_speed

def soft_stop(motor):
    bump = 0.5 * (1 if motor.throttle and motor.throttle > 0 else -1)
    motor.throttle = bump
    time.sleep(0.05)
    motor.throttle = 0

def move_forward(speed=1):
    soft_start(kit.motor1, -speed)
    soft_start(kit.motor3, -speed)

def move_backward(speed=1):
    soft_start(kit.motor1, speed)
    soft_start(kit.motor3, speed)

def turn_left(speed=1):
    soft_start(kit.motor1, -speed)
    soft_start(kit.motor3, speed)

def turn_right(speed=1):
    soft_start(kit.motor1, speed)
    soft_start(kit.motor3, -speed)

def stop():
    soft_stop(kit.motor1)
    soft_stop(kit.motor3)
