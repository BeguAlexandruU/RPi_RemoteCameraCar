from machine import Pin, ADC, SPI
import struct  # Required to pack data into bytes
from picozero import LED, Button
import nrf24l01
from time import sleep


NRF_RX_ADDRESS = b"Pico1"
nrf = None

j1_x_adc = None
j1_y_adc = None
j2_x_adc = None
j2_y_adc = None

j1_button = None
j2_button = None

led_green = None
led_red = None

def setup():
    global nrf, j1_x_adc, j1_y_adc, j2_x_adc, j2_y_adc, led_green, led_red, j1_button, j2_button
    print("Setting up NRF24L01 and ADCs...")
    
    # Initialize NRF24L01
    spi = SPI(1, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
    nrf = nrf24l01.NRF24L01(spi, cs=Pin(13), ce=Pin(9), channel=108, payload_size=4)

    nrf.set_power_speed(nrf24l01.POWER_2, nrf24l01.SPEED_250K)
    nrf.open_tx_pipe(NRF_RX_ADDRESS) 
    nrf.stop_listening()

    # Initialize ADCs
    j1_x_adc = ADC(Pin(28))
    j1_y_adc = ADC(Pin(29))
    j2_x_adc = ADC(Pin(27))
    j2_y_adc = ADC(Pin(26))
    
    # Initialize Buttons
    j1_button = Button(7)
    j2_button = Button(15)
    j1_button.when_released = lambda: send_button_notification(1)
    j2_button.when_released = lambda: send_button_notification(2)

    # Initialize LEDs
    led_green = LED(0)
    led_red   = LED(1)
    
    print("Setup complete.")

def send_button_notification(button_id):
    global nrf
    
    # Send special packet for button press: (button_id, 127, 127, 127)
    # Using 127 as a marker to distinguish from joystick data (-100 to 100)
    data = {
        'type': 'button',
        'button_id': button_id
    }
    send_data(data)
    

def set_leds(green_on, red_on):
    if green_on:
        led_green.on()
    else:
        led_green.off()
        
    if red_on:
        led_red.on()
    else:
        led_red.off()
  

def map_range(value):
  
    # Input range
    in_min = 0
    in_max = 65535
    out_min = -100
    out_max = 100
    
    # Calculate span
    span = in_max - in_min
    if span == 0: return out_min
    
    # Map the value
    return (value - in_min) * (out_max - out_min) // span + out_min

def send_data(data):
    global nrf
    
    if data['type'] == 'joystick':
        j1_x, j1_y, j2_x, j2_y = data['values']
        payload = struct.pack("bbbb", j1_x, j1_y, j2_x, j2_y)
    elif data['type'] == 'button':
        button_id = data['button_id']
        payload = struct.pack("bbbb", button_id, 127, 127, 127)

    # 4. Send Data
    try:
        # success
        nrf.send(payload)
        set_leds(green_on=True, red_on=False)
    except OSError:
        # failure
        print("Error: NRF24L01 Send Failed")
        set_leds(green_on=False, red_on=True)

if __name__ == "__main__":
    setup()
    
    print("Starting main loop...")
    while True:
        # Read joystick values
        j1_x = map_range(j1_x_adc.read_u16())
        j1_y = map_range(j1_y_adc.read_u16())
        j2_x = map_range(j2_x_adc.read_u16())
        j2_y = map_range(j2_y_adc.read_u16())
        
        # Prepare data
        data = {
            'type': 'joystick',
            'values': (j1_x, j1_y, j2_x, j2_y)
        }
        
        # Send data
        send_data(data)
        
    


