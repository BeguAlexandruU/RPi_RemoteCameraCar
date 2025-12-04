from gpiozero import LED, TonalBuzzer
from time import sleep
import threading

# Initialize GPIO pins
red_led = None    
blue_led = None     
speaker = None

def setup():
    """Initialize all IOs"""
    print("Setting up LEDs and Speaker...")
    red_led = LED(17)      
    blue_led = LED(27)       
    speaker = TonalBuzzer(22) 
    
    red_led.off()
    blue_led.off()
    speaker.stop()
    print("IO setup complete.")

def flash_red_led(times, interval):
    """Flash the red LED a specified number of times."""
    def flash():
        for _ in range(times):
            red_led.on()
            sleep(interval)
            red_led.off()
            sleep(interval)
    threading.Thread(target=flash).start()

def stop_all():
    """Turn off all IOs"""
    red_led.off()
    blue_led.off()
    speaker.stop()
