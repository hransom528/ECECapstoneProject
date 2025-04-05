import board
import time
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

def smooth_throttle(motor, target_speed, step=0.05, delay=0.02):
    """
    Gradually ramp throttle from current value to target_speed.
    """
    current = motor.throttle or 0  # handle None
    steps = int(abs(target_speed - current) / step) + 1
    for i in range(steps):
        new_val = current + step * (1 if target_speed > current else -1)
        motor.throttle = max(min(new_val, 1), -1)
        current = motor.throttle
        time.sleep(delay)
    motor.throttle = target_speed  # ensure it hits exact target

def move_forward(speed=1):
    smooth_throttle(kit.motor1, -speed)
    smooth_throttle(kit.motor3, -speed)

def move_backward(speed=1):
    smooth_throttle(kit.motor1, speed)
    smooth_throttle(kit.motor3, speed)

def turn_left(speed=1):
    smooth_throttle(kit.motor1, -speed)
    smooth_throttle(kit.motor3, speed)

def turn_right(speed=1):
    smooth_throttle(kit.motor1, speed)
    smooth_throttle(kit.motor3, -speed)

def stop():
    smooth_throttle(kit.motor1, 0)
    smooth_throttle(kit.motor3, 0)
