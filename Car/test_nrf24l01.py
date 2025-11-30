import time
import struct
import board
import busio
from digitalio import DigitalInOut
from gpiozero import Servo
from adafruit_nrf24l01 import RF24

# --- Configurare Pini pentru CircuitPython (NRF24) ---
# Pe RPi, board.SCK, board.MOSI, board.MISO sunt pinii hardware SPI
# Definim pinii CE și CSN
ce_pin = DigitalInOut(board.D17)  # GPIO 17 (Pin fizic 11)
csn_pin = DigitalInOut(board.D8)  # GPIO 8  (Pin fizic 24)

# --- Configurare SPI și NRF24L01 ---
try:
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    nrf = RF24(spi, cs=csn_pin, ce=ce_pin)
    
    # Setări NRF (aceleași ca pe Pico)
    nrf.data_rate = 0.250 # 250 kbps (echivalent cu SPEED_250K)
    nrf.pa_level = 0      # Putere maximă (0 = max, -6, -12, -18)
    nrf.payload_length = 4
    nrf.open_rx_pipe(1, b"Pico1")
    nrf.listen = True
    print("NRF24L01 inițializat cu succes.")
except Exception as e:
    print(f"Eroare la inițializarea radio: {e}")

# --- Configurare Servomotoare (gpiozero) ---
# Corecție puls: Standardele sunt de obicei min=1ms, max=2ms. 
# Unele servo ieftine merg 0.5ms - 2.5ms. Ajustează aici dacă servo bârâie.
# frame_width=0.02 (20ms) este standard.
my_correction = 0.45
max_pw = (2.0 + my_correction) / 1000
min_pw = (1.0 - my_correction) / 1000
 
servo_x = Servo(22, min_pulse_width=min_pw, max_pulse_width=max_pw) # GPIO 22
servo_y = Servo(27, min_pulse_width=min_pw, max_pulse_width=max_pw) # GPIO 27

# --- Variabile de Control ---
DEAD_ZONE = 3
SMOOTH_FACTOR = 0.1 # Pe Linux e bine să fie puțin mai mare pentru stabilitate

# Servo în gpiozero variază de la -1 la 1.
# 0 este centrul.
current_x_value = 0.0 
current_y_value = 0.0

print("Receiver ready (Pi Zero W), waiting for data...")

while True:
    try:
        # Verificăm dacă avem date în buffer
        if nrf.available():
            # Citim payload-ul
            package = nrf.read()
            
            if package:
                try:
                    # Unpack: 4 bytes (valori -100 la 100)
                    j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", package)
                    
                    print(f"RX: X:{j1_x} Y:{j1_y}")

                    # --- X-Axis Logic ---
                    if abs(j1_x) >= DEAD_ZONE:
                        # gpiozero vrea -1 la 1. Joystick-ul dă -100 la 100.
                        # Împărțim la 100 simplu.
                        target_x = j1_x / 100.0
                        
                        # Interpolare (Smoothing)
                        current_x_value += (target_x - current_x_value) * SMOOTH_FACTOR
                    
                    # --- Y-Axis Logic ---
                    if abs(j1_y) >= DEAD_ZONE:
                        target_y = j1_y / 100.0
                        current_y_value += (target_y - current_y_value) * SMOOTH_FACTOR

                    # --- Aplicare poziții ---
                    # Ne asigurăm că nu depășim limitele -1 / 1
                    current_x_value = max(min(current_x_value, 1), -1)
                    current_y_value = max(min(current_y_value, 1), -1)

                    servo_x.value = current_x_value
                    servo_y.value = current_y_value

                except Exception as e:
                    print(f"Eroare procesare pachet: {e}")

        # Sleep mic pentru a nu ține procesorul la 100%
        time.sleep(0.01)

    except KeyboardInterrupt:
        print("Oprire...")
        break
    except Exception as e:
        print(f"Eroare generală: {e}")
        time.sleep(0.5)