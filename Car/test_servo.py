from gpiozero import Servo
from time import sleep

camera_servo_hor = Servo(21)  
camera_servo_ver = Servo(20)  

while True:
    for pos in range(-100, 101, 20):
        camera_servo_hor.value = pos / 100  
        camera_servo_ver.value = pos / 100  
        print(f"Setting servos to position: {pos}")
        sleep(0.5)