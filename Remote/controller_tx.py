from machine import Pin, ADC, SPI
import time
import struct  # Required to pack data into bytes
import nrf24l01

# --- Setup Hardware ---
spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
nrf = nrf24l01.NRF24L01(spi, cs=Pin(1), ce=Pin(0), channel=108, payload_size=4)

nrf.set_power_speed(nrf24l01.POWER_2, nrf24l01.SPEED_250K)
nrf.open_tx_pipe(b"Pico1") 
nrf.stop_listening() # We are the transmitter, so we stop listening

# Initialize ADCs
j1_x_adc = ADC(Pin(26))
j1_y_adc = ADC(Pin(27))
j2_x_adc = ADC(Pin(28))
# Note: GP29 is usually VSYS (System Voltage) on Pico, not a free ADC.
# This might read static noise or battery voltage depending on your board.
j2_y_adc = ADC(Pin(29)) 

def map_range(value, in_min, in_max, out_min, out_max):
    # Determine the range span
    span = in_max - in_min
    if span == 0: return out_min
    # Map the value
    return (value - in_min) * (out_max - out_min) // span + out_min

while True:
    # 1. Read Raw Data
    j1_x_raw = j1_x_adc.read_u16()
    j1_y_raw = j1_y_adc.read_u16()
    j2_x_raw = j2_x_adc.read_u16()
    j2_y_raw = j2_y_adc.read_u16()

    # 2. Map to -100 to 100
    j1_x = map_range(j1_x_raw, 0, 65535, -100, 100)
    j1_y = map_range(j1_y_raw, 0, 65535, -100, 100)
    j2_x = map_range(j2_x_raw, 0, 65535, -100, 100)
    j2_y = map_range(j2_y_raw, 0, 65535, -100, 100)

    # 3. Pack Data
    # 'b' = signed char (1 byte, range -128 to 127). Perfect for -100 to 100.
    # We pack 4 values: "bbbb"
    payload = struct.pack("bbbb", j1_x, j1_y, j2_x, j2_y)

    # 4. Send Data
    try:
        nrf.send(payload)
        #print(f"Sent: {j1_x}, {j1_y}, {j2_x}, {j2_y}")
    except OSError:
        print("Error: NRF24L01 Send Failed (Check wiring/Power)")

    #time.sleep(0.01) # Send roughly 20 times a second
