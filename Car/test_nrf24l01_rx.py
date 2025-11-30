import argparse
from datetime import datetime
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *
from nrf24 import RF24

# --- Configuratii Hardware ---
# Pinii BCM la care sunt conectate Servomotoarele
SERVO_X_PIN = 27 
SERVO_Y_PIN = 22 # Am pastrat 22 din discutiile anterioare (in loc de 28)

# Pinii BCM pentru NRF24L01:
# CE trebuie sa fie BCM (exemplu: 25, 17, sau 22)
NRF_CE_PIN = 25 # Schimba acest pin daca ai legat CE la altceva (e.g., 17 sau 22)
# CSN este gestionat de pigpio (de obicei pinul hardware SPI, BCM 8)

# --- Variabile de Control ---
# Adresa de receptie trebuie sa se potriveasca cu cea a transmitatorului (4 caractere ASCII)
RECEIVE_ADDRESS = 'Pico' 
DEAD_ZONE = 5        # Ignoram miscarile mici ale joystick-ului (-5 la 5)
SMOOTH_FACTOR = 0.1  # Nivel de amortizare (0.1 = lent/lin)

# Pozitii curente Servo (Valori -1.0 la 1.0)
current_x = 0.0
current_y = 0.0

# --- Functie de Mapare Servo (PWM) ---
def map_servo_value_to_pwm(value):
    """ Mapeaza valoarea servo (-1.0 la 1.0) la latimea pulsului in microsecunde (1000 la 2000). """
    # PWM standard pentru servo (1000us = min, 1500us = centru, 2000us = max)
    MIN_PULSE = 1000
    MAX_PULSE = 2000
    
    # Valoarea de intrare (value) e intre -1 si 1. O aducem la 0-2 (value + 1)
    # Apoi o mapam la latimea pulsului: (Valoare * (Diferenta PWM / 2)) + MIN_PULSE
    return int(((value + 1.0) * (MAX_PULSE - MIN_PULSE) / 2.0) + MIN_PULSE)


if __name__ == "__main__":

    print("Python NRF24 Receiver for Servo Control.")
    
    # --- 1. Initializare pigpio ---
    parser = argparse.ArgumentParser(prog="receiver_servo.py", description="NRF24 Receiver for Servo Control.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost', help="Hostname for the Raspberry running the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    
    args = parser.parse_args()
    hostname = args.hostname
    port = args.port

    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye. Check if 'sudo pigpiod' is running.")
        sys.exit()

    # --- 2. Setup Servomotoare ---
    # Seteaza frecventa PWM la 50 Hz (standard pentru servo)
    pi.set_PWM_frequency(SERVO_X_PIN, 50)
    pi.set_PWM_frequency(SERVO_Y_PIN, 50)
    
    # Seteaza servo la pozitia initiala (Centru: 1500 us)
    pi.set_servo_pulsewidth(SERVO_X_PIN, 1500)
    pi.set_servo_pulsewidth(SERVO_Y_PIN, 1500)
    
    print(f"Servos on BCM {SERVO_X_PIN} and {SERVO_Y_PIN} initialized to center.")


    # --- 3. Initializare NRF24 ---
    nrf = NRF24(pi, ce=NRF_CE_PIN, payload_size=RF24_PAYLOAD.DYNAMIC, channel=108, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MAX)
    
    # Asigura-te ca lungimea adresei se potriveste cu TX (e.g. 4 pentru 'Pico')
    nrf.set_address_bytes(len(RECEIVE_ADDRESS)) 

    # Asculta pe adresa specificata (Pipe 1)
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, RECEIVE_ADDRESS)
    
    # Seteaza canalul la 108 pentru a se potrivi cu configuratia initiala (daca TX foloseste Pico/MicroPython)
    nrf.set_channel(108)

    print(f"NRF24 Listening on address: {RECEIVE_ADDRESS}")

    # --- 4. Loop de Receptie si Control Servo ---
    try:
        while True:
            # Cat timp datele sunt gata, proceseaza-le
            while nrf.data_ready():
                
                pipe = nrf.data_pipe()
                payload = nrf.get_payload()
                
                # Asteptam 4 bytes: j1_x, j1_y, j2_x, j2_y (de la -100 la 100)
                if len(payload) == 4:
                    try:
                        # Despacheteaza 4 valori signed char ("bbbb")
                        j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", payload)
                        
                        # Debugging:
                        # print(f"RX -> J1_X: {j1_x}, J1_Y: {j1_y}")

                        global current_x, current_y
                        
                        # --- Logica Axa X ---
                        if abs(j1_x) > DEAD_ZONE:
                            target_x = j1_x / 100.0
                            current_x += (target_x - current_x) * SMOOTH_FACTOR
                        
                        # --- Logica Axa Y ---
                        if abs(j1_y) > DEAD_ZONE:
                            target_y = j1_y / 100.0
                            current_y += (target_y - current_y) * SMOOTH_FACTOR

                        # Limiteaza valorile strict intre -1.0 si 1.0
                        current_x = max(min(current_x, 1.0), -1.0)
                        current_y = max(min(current_y, 1.0), -1.0)
                        
                        # Aplica pozitia prin PWM
                        pwm_x = map_servo_value_to_pwm(current_x)
                        pwm_y = map_servo_value_to_pwm(current_y)
                        
                        pi.set_servo_pulsewidth(SERVO_X_PIN, pwm_x)
                        pi.set_servo_pulsewidth(SERVO_Y_PIN, pwm_y)

                        print(f"RX: X:{j1_x}, Y:{j1_y} | Servo PWM X:{pwm_x}, Y:{pwm_y}")
                        
                    except struct.error:
                        print(f"Eroare la despachetare. Pachet corupt.")
                
                else:
                    print(f"Pachet primit de {len(payload)} bytes. Ignorat.")

            # Pauza scurta de 10 ms (ajustata de la 100ms)
            time.sleep(0.01)
            
    except Exception as e:
        print(f"A aparut o eroare majora: {e}")
        traceback.print_exc()
    finally:
        # Oprire Servo si NRF la iesirea din program
        nrf.power_down()
        pi.set_servo_pulsewidth(SERVO_X_PIN, 0) # Opreste pulsul PWM
        pi.set_servo_pulsewidth(SERVO_Y_PIN, 0)
        pi.stop()