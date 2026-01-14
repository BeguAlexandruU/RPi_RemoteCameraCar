from gpiozero import LED, TonalBuzzer
from time import sleep
import threading

# Initialize GPIO pins
red_led = None    
blue_led = None     
speaker = None
flashing_red = False

def setup():
    global red_led, blue_led, speaker
    """Initialize all IOs"""
    print("Setting up LEDs and Speaker...")
    red_led = LED(26)      
    blue_led = LED(19)       
    speaker = TonalBuzzer(16) 
    
    red_led.off()
    blue_led.off()
    speaker.stop()
    
    print("IO setup complete.")

def start_flash_led():
    """Start flashing the red LED continuously."""
    
    print("Started flashing red LED.....")
    global flashing_red, red_led
    flashing_red = True
    def flash():
        while flashing_red:
            for _ in range(2):
                red_led.on()
                sleep(0.1)
                red_led.off()
                sleep(0.1)
            for _ in range(2):
                blue_led.on()
                sleep(0.1)
                blue_led.off()
                sleep(0.1)
    threading.Thread(target=flash).start()
    
    print("Started flashing red LED.!")

def stop_flash_led():
    """Stop flashing the red LED."""
    global flashing_red
    flashing_red = False

def stop_all():
    """Turn off all IOs"""
    global flashing_red
    flashing_red = False
    red_led.off()
    blue_led.off()
    speaker.stop()
