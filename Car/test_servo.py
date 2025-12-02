from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep


factory = PiGPIOFactory()

camera_servo_hor = AngularServo(21, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)  
camera_servo_ver = AngularServo(20, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)  

def set_servo_pos(hor_val, ver_val):
    # Map input range [-100, 100] to servo angle [0, 180]
    def map_to_angle(v):
        # clamp
        if v < -100:
            v = -100
        if v > 100:
            v = 100
        # Map [-100,100] -> [-90,90]
        return v * 0.9

    hor_angle = map_to_angle(hor_val)
    ver_angle = map_to_angle(ver_val)

    # Assign angles (degrees)
    camera_servo_hor.angle = hor_angle
    camera_servo_ver.angle = ver_angle

while True:
    for pos in range(-100, 101, 20):
        set_servo_pos(pos, pos)
        mapped = pos * 0.9
        print(f"Setting servos raw: {pos} -> mapped angle: {mapped:.1f}°")
        sleep(0.5)