from datetime import datetime
from gc import enable
import struct
import sys
import time
import traceback

import pigpio
from gpiozero import Motor, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from nrf24 import *

HOSTNAME = "localhost"
PORT = 8888
NRF_RX_ADDRESS = b"Pico1"

nrf = None

camera_servo_hor = None
camera_servo_ver = None

motor_left = None
motor_right = None

def setup():
    global nrf, camera_servo_hor, camera_servo_ver, motor_left, motor_right
    
    print("Setting up NRF24L01, Motors, and Camera Servos...")
    
    # Initialize NRF24L01
    nrf = NRF24(pi, ce=7, payload_size=4, channel=108, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=1) # type: ignore
    nrf.set_address_bytes(len(NRF_RX_ADDRESS))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, NRF_RX_ADDRESS) # type: ignore
    
    # Initialize Motors
    motor_left = Motor(forward=18, backward=15, enable=14)
    motor_right = Motor(forward=23, backward=24, enable=25)
    
    # Initialize Camera Servos
    factory = PiGPIOFactory()
    camera_servo_hor = AngularServo(21, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)  
    camera_servo_ver = AngularServo(20, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)  
    
    print("Setup complete.")

def set_motor_input(x_axis, y_axis):
    # y_axis: forward/backward
    # x_axis: left/right
    
    left_speed = y_axis + x_axis
    right_speed = y_axis - x_axis
    
    
    # Clamp speeds to [-100, 100]
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))
    
    set_motor_speed(left_speed, right_speed)

def set_motor_speed(left_speed, right_speed):
    # Set left motor speed
    if left_speed > 0:
        motor_left.forward(left_speed / 100)
    elif left_speed < 0:
        motor_left.backward(-left_speed / 100)
    else:
        motor_left.stop()
    
    # Set right motor speed
    if right_speed > 0:
        motor_right.forward(right_speed / 100)
    elif right_speed < 0:
        motor_right.backward(-right_speed / 100)
    else:
        motor_right.stop()

def set_camera_servo_input(hor_pos, ver_pos):
    def map_to_angle(v):
        # clamp
        if v < -100:
            v = -100
        if v > 100:
            v = 100
        # Map [-100,100] -> [-90,90]
        return v * 0.9

    hor_angle = map_to_angle(hor_pos * -1)
    ver_angle = map_to_angle(ver_pos)

    # Assign angles (degrees)
    camera_servo_hor.angle = hor_angle
    camera_servo_ver.angle = ver_angle
    
    
if __name__ == "__main__":
    
    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {HOSTNAME}:{PORT} ...')
    pi = pigpio.pi(HOSTNAME, PORT)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    setup()

    # Enter a loop receiving data on the address specified.
    try:
        print(f'Receive from {NRF_RX_ADDRESS}')
        while True:

            # As long as data is ready for processing, process it.
            while nrf.data_ready():
                
                # Read pipe and payload for message.
                pipe = nrf.data_pipe()
                payload = nrf.get_payload()    


                j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", payload)
        
                print(f"Received - J1_X: {j1_x}, J1_Y: {j1_y}, J2_X: {j2_x}, J2_Y: {j2_y}")
                
                set_camera_servo_input(j1_x, j1_y)
                
                set_motor_input(j2_x, j2_y)
                
                
            # Sleep 100 ms.
            # time.sleep(0.1)
    except:
        traceback.print_exc()
        nrf.power_down()
        pi.stop()
