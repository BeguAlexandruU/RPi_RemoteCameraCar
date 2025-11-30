import time
import struct
import board
import digitalio
from gpiozero import Servo
from circuitpython_nrf24l01.rf24 import RF24

# --- 1. Configurare Pini și SPI (Stilul din exemplul tău) ---
# Pe Linux/RPi, folosim librăria "board" care detectează automat pinii Hardware SPI
# SPI_BUS va folosi automat SCK (GPIO 11), MOSI (GPIO 10), MISO (GPIO 9)
spi = board.SPI()

# Definim pinii CE și CSN folosind DigitalInOut (pentru control rapid)
# CSN la GPIO 8 (Pin fizic 24 - CE0)
# CE la GPIO 17 (Pin fizic 11) - Poți schimba dacă ai legat altundeva
csn_pin = digitalio.DigitalInOut(board.D8)
ce_pin = digitalio.DigitalInOut(board.D17)

# Inițializăm NRF24L01
nrf = RF24(spi, csn_pin, ce_pin)

# --- 2. Setări Radio (Să se potrivească cu Transmițătorul) ---
nrf.data_rate = 0.250       # 250 kbps (nrf24l01.SPEED_250K)
nrf.pa_level = 0            # 0 dBm (Putere maximă)
nrf.payload_length = 4      # Primim exact 4 bytes (j1_x, j1_y, j2_x, j2_y)
nrf.open_rx_pipe(1, b"Pico1") # Adresa trebuie să fie identică cu cea din TX
nrf.listen = True           # Intră în mod recepție

print("Radio inițializat. Aștept date...")

# --- 3. Configurare Servomotoare (gpiozero) ---
# Pinii pentru Servo (GPIO BCM)
SERVO_X_PIN = 27
SERVO_Y_PIN = 22  # Am schimbat 28 cu 22 deoarece RPi Zero nu are GPIO 28 accesibil ușor

# Ajustare pulsuri: Standard e 1ms-2ms. 
# Dacă servo nu face cursa completă, poți încerca min=0.5ms (0.0005) și max=2.5ms (0.0025)
servo_x = Servo(SERVO_X_PIN, min_pulse_width=0.001, max_pulse_width=0.002)
servo_y = Servo(SERVO_Y_PIN, min_pulse_width=0.001, max_pulse_width=0.002)

# --- 4. Variabile de Logică ---
DEAD_ZONE = 5        # Ignorăm mișcările mici ale joystick-ului (-5 la 5)
SMOOTH_FACTOR = 0.1  # Cât de lin se mișcă (0.1 = lent/lin, 1.0 = instant)

current_x = 0.0      # Poziția curentă servo (-1 la 1)
current_y = 0.0

while True:
    try:
        # Verificăm dacă avem date disponibile
        if nrf.available():
            # Citim payload-ul (lista de bytes)
            buffer = nrf.read()
            
            # Ne asigurăm că am primit date valide
            if buffer is None:
                continue

            try:
                # Despachetăm cei 4 bytes (valori semnate -128 la 127)
                # Joystick-ul trimite probabil -100 la 100
                j1_x, j1_y, j2_x, j2_y = struct.unpack("bbbb", buffer)
                
                print(f"RX -> J1_X: {j1_x}, J1_Y: {j1_y}")

                # --- Logica Axa X ---
                if abs(j1_x) > DEAD_ZONE:
                    # Mapăm -100...100 la -1...1
                    target_x = j1_x / 100.0
                    # Interpolare pentru mișcare fluidă
                    current_x += (target_x - current_x) * SMOOTH_FACTOR
                
                # --- Logica Axa Y ---
                if abs(j1_y) > DEAD_ZONE:
                    target_y = j1_y / 100.0
                    current_y += (target_y - current_y) * SMOOTH_FACTOR

                # --- Aplicare pe Servo ---
                # Limităm valorile strict între -1 și 1 pentru a evita erorile gpiozero
                current_x = max(min(current_x, 1.0), -1.0)
                current_y = max(min(current_y, 1.0), -1.0)
                
                servo_x.value = current_x
                servo_y.value = current_y

            except struct.error:
                print("Eroare la despachetare date (struct invalid)")

        # Pauză mică pentru a nu ține CPU la 100%
        time.sleep(0.01)

    except KeyboardInterrupt:
        print("Oprire program...")
        nrf.listen = False
        break
    except Exception as e:
        print(f"Eroare neașteptată: {e}")
        time.sleep(0.5)