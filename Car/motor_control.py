
from gpiozero import Motor
from state_control import get_speed_limit

motor_left = None
motor_right = None

def setup():
    global motor_left, motor_right
    motor_left = Motor(forward=18, backward=17, enable=14)
    motor_right = Motor(forward=23, backward=24, enable=25)

def set_motor_input(x_axis, y_axis):
    # y_axis: forward/backward
    # x_axis: left/right
    
    left_speed = y_axis + (x_axis * 0.4)
    right_speed = y_axis - (x_axis * 0.4)
    
    
    # Clamp speeds to [-100, 100]
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))
    
    set_motor_speed(left_speed, right_speed)

def set_motor_speed(left_speed, right_speed):
    # Apply speed limit from current state
    speed_limit = get_speed_limit()
    
    left_speed = (left_speed / 100.0) * speed_limit
    right_speed = (right_speed / 100.0) * speed_limit
    
    # Clamp speeds to [-1, 1] for motor controller
    left_speed = max(-1.0, min(1.0, left_speed))
    right_speed = max(-1.0, min(1.0, right_speed))
    
    # Set left motor speed
    if left_speed > 0:
        motor_left.forward(left_speed)
    elif left_speed < 0:
        motor_left.backward(-left_speed)
    else:
        motor_left.stop()
    
    # Set right motor speed
    if right_speed > 0:
        motor_right.forward(right_speed)
    elif right_speed < 0:
        motor_right.backward(-right_speed)
    else:
        motor_right.stop()

def stop_motors():
    """Immediately stop both motors (fail-safe)"""
    motor_left.stop()
    motor_right.stop()