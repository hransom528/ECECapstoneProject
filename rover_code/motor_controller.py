import time
import math

try:
    import board
except ModuleNotFoundError as e:
    print(f"[WARNING] Failed to initialize the board: {e}")
    kit = None
except OSError as e:
    print(f"[WARNING] Failed to initialize the board: {e}")
    kit = None

try:
    from adafruit_motorkit import MotorKit
    kit = MotorKit(i2c=board.I2C())
except ValueError as e:
    print(f"[WARNING] Failed to initialize MotorKit: {e}")
    kit = None
except OSError as e:
    print(f"[WARNING] I2C device not found or not responding: {e}")
    kit = None
except ModuleNotFoundError as e:
    print(f"[WARNING] Adafruit Motorkit module is not installed: {e}")

def ease_in_out_quad(t):
    """Quadratic easing function."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t

def soft_start(motor, target_speed, duration):
    steps = 20  # More steps = smoother
    step_time = duration / steps
    for i in range(steps):
        t = i / (steps - 1)
        eased = ease_in_out_quad(t)
        motor.throttle = target_speed * eased
        time.sleep(step_time)

def soft_stop(motor, duration):
    steps = 20
    step_time = duration / steps
    start_speed = motor.throttle or 0
    for i in range(steps):
        t = i / (steps - 1)
        eased = ease_in_out_quad(1 - t)  # Reverse easing for deceleration
        motor.throttle = start_speed * eased
        time.sleep(step_time)
    motor.throttle = 0

def move_with_soft(motor1, motor1_speed, motor3, motor3_speed, total_duration):
    ramp_duration = total_duration * 0.15  # 15% for start, 15% for stop
    run_duration = total_duration * 0.7        # 70% full speed
    
    # Soft start
    soft_start(motor1, motor1_speed, ramp_duration)
    soft_start(motor3, motor3_speed, ramp_duration)
    
    # Full speed
    motor1.throttle = motor1_speed
    motor3.throttle = motor3_speed
    time.sleep(run_duration)
    
    # Soft stop
    soft_stop(motor1, ramp_duration)
    soft_stop(motor3, ramp_duration)

def move_forward(duration, speed):
    move_with_soft(kit.motor1, -speed, kit.motor3, -speed, duration)

def move_backward(duration, speed):
    move_with_soft(kit.motor1, speed, kit.motor3, speed, duration)

def turn_left(duration, speed):
    move_with_soft(kit.motor1, -speed, kit.motor3, speed, duration)  # Left motor backward, right motor forward

def turn_right(duration, speed):
    move_with_soft(kit.motor1, speed, kit.motor3, -speed, duration)  # Left motor forward, right motor backward

def stop():
    soft_stop(kit.motor1, 0.15)  # optional: set a small soft stop time
    soft_stop(kit.motor3, 0.15)