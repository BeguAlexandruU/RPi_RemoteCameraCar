from datetime import datetime
from gc import enable
import struct
import sys
import time
import traceback
import pigpio

import io_control
import state_control
import nrf24_module
import motor_control
import servo_control

HOSTNAME = "localhost"
PORT = 8888

def setup():
    print("Setting up NRF24L01, Motors, and Camera Servos...")
    
    # Initialize NRF24L01
    nrf24_module.setup(pi)
    
    # Initialize Motors
    motor_control.setup()
    
    # Initialize Camera Servos
    servo_control.setup()
    
    # Indicate setup complete
    io_control.setup()
    
    print("Setup complete.")


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
        print(f'Receive from {nrf24_module.NRF_RX_ADDRESS}')
        while True:

            # As long as data is ready for processing, process it.
            while nrf24_module.nrf.data_ready():
                
                # Read pipe and payload for message.
                pipe = nrf24_module.nrf.data_pipe()
                payload = nrf24_module.nrf.get_payload()    

                j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", payload)
        
                # print(f"Received - J1_X: {j1_x}, J1_Y: {j1_y}, J2_X: {j2_x}, J2_Y: {j2_y}")
                
                if j1_y == 127 and j2_x == 127 and j2_y == 127:
                    # Button press detected, ignore joystick input for servos
                    if j1_x == 1:
                        state_control.switch_state()
                        print(f"Received: {j1_x}")
                        # state_control.print_state()
                else:
                    servo_control.set_servo_input(j1_x, j1_y)
                    motor_control.set_motor_input(j2_x, j2_y)
                
                
            # Sleep 100 ms.
            # time.sleep(0.1)
    except:
        traceback.print_exc()
        nrf24_module.nrf.power_down()
        pi.stop()
