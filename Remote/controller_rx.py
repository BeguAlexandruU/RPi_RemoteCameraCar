from machine import Pin, ADC, SPI
import time
from lib.picozero import Servo
import struct
import nrf24l01

# --- Servo Setup ---
# Initialize Servos (using standard Pico PWM pins for Pico Zero)
servo_y = Servo(28, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo_x = Servo(27, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

# --- NRF24L01 Setup ---
# Note: You defined SPI(0) twice with different pins. We will use the second definition:
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
# Remember to adjust payload_size to 4 if the transmitter is sending only 4 bytes.
nrf = nrf24l01.NRF24L01(spi, cs=Pin(17), ce=Pin(20), channel=108, payload_size=4) 

# Configure to match transmitter's speed (if TX was optimized to 2M, use 2M here)
nrf.set_power_speed(nrf24l01.POWER_2, nrf24l01.SPEED_250K) 
nrf.open_rx_pipe(1, b"Pico1") 
nrf.start_listening()

# --- Control Variables ---
DEAD_ZONE = 3    # New: Ignore joystick values between -5 and 5. This "saves" the position.
SMOOTH_FACTOR = 0.05  # New: Lower value = smoother/slower movement (e.g., 0.1 to 0.5)

# Initialize current servo positions to prevent jumping on startup
current_x_value = 0.5 # Servo value range: 0.0 to 1.0 (center)
current_y_value = 0.5

print("Receiver ready, waiting for data...")

while True:
    if nrf.any():
        package = nrf.recv()
        
        try:
            # Unpack the 4 bytes (joystick values range -100 to 100)
            j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", package)
            
            print(f"Received - J1_X: {j1_x}, J1_Y: {j1_y}, J2_X: {j2_x}, J2_Y: {j2_y}")
            
            # --- X-Axis Logic ---
            if abs(j1_x) >= DEAD_ZONE:
                # 1. Map the joystick value (-100 to 100) to the target servo range (0.0 to 1.0)
                target_x_value = (j1_x + 100) / 200 
                
                # 2. Smooth the movement (Interpolation)
                current_x_value += (target_x_value - current_x_value) * SMOOTH_FACTOR
            
            # --- Y-Axis Logic ---
            if abs(j1_y) >= DEAD_ZONE:
                target_y_value = (j1_y + 100) / 200
                current_y_value += (target_y_value - current_y_value) * SMOOTH_FACTOR

            # --- Apply New Positions ---
            servo_x.value = current_x_value
            servo_y.value = current_y_value
            
        except Exception as e:
            # Catch both struct unpack errors and NRF related issues
            print(f"Packet/Servo Error: {e}")

    # Small sleep is good here to yield control back to the operating system
    # (MicroPython) and prevent over-taxing the processor.
    time.sleep(0.005)