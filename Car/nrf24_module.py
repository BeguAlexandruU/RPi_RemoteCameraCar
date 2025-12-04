from nrf24 import *


NRF_RX_ADDRESS = b"Pico1"

nrf = None

def setup():
    global nrf
    
    print("Setting up NRF24L01...")
    
    # Initialize NRF24L01
    nrf = NRF24(pi, ce=7, payload_size=4, channel=108, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=1) # type: ignore
    nrf.set_address_bytes(len(NRF_RX_ADDRESS))
    nrf.open_reading_pipe(RF24_RX_ADDR.P1, NRF_RX_ADDRESS) # type: ignore
    
    print("Setup complete.")
    
    