import time
from gpiozero import Motor

motor_left = Motor(forward=15, backward=18, enable=14)
motor_right = Motor(forward=23, backward=24, enable=25)

while True:
    for speed in range(-100, 101, 20):
        if speed > 0:
            motor_left.forward(speed / 100)
            motor_right.forward(speed / 100)
        elif speed < 0:
            motor_left.backward(-speed / 100)
            motor_right.backward(-speed / 100)
        else:
            motor_left.stop()
            motor_right.stop()
        time.sleep(0.5)