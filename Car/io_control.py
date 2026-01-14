from gpiozero import LED, TonalBuzzer
from time import sleep
import threading

# ///////////////////melody data
melody_introduction = ['A#4', 'A#4', 'A#4', 'A#4',]
durations_introduction = [4, 4, 4, 4]

melody = [
  # Motive principal (bar 1–2)
  'A#4', 'B4', 'D#5', 'A#4', 'A#4',
  'A#4', 'B4', 'D#5', 'A#4', 'A#4',
  'A#4', 'B4', 'D#5', 'A#4', 'A#4',
  'A#4', 'B4', 'D#5', 'F5', 'F5',
  'G#5', 'F#5', 'F5', 'D#5', 'D#5',
  'G#5', 'F#5', 'F5', 'D#5', 'D#5',
]


durations = [
  # toate sunt optimi (8) pentru început – trap steady flow
  5, 5, 8, 4, 4,
  5, 5, 8, 4, 4,
  5, 5, 8, 4, 4,
  5, 5, 8, 4, 4,
  5, 5, 8, 4, 4,
  5, 5, 8, 4, 4,
]

listen_mus2 = []
for note, dur in zip(melody_introduction, durations_introduction):
    # Convert duration: assuming 1.0 is a quarter note, so 8 means 1/8th note, so 0.5
    duration_val = 1.8/dur  # 4/8=0.5, 4/16=0.25, etc.
    listen_mus2.append([note, duration_val])

liten_mus = []
for note, dur in zip(melody, durations):
    # Convert duration: assuming 1.0 is a quarter note, so 8 means 1/8th note, so 0.5
    duration_val = 1.8/dur  # 4/8=0.5, 4/16=0.25, etc.
    liten_mus.append([note, duration_val])
    
# ///////////////////end melody data

# Initialize GPIO pins
red_led = None    
blue_led = None     
flashing_led = False

speaker = None
playing_melody = False


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
    global flashing_led, red_led
    flashing_led = True
    def flash():
        
        while flashing_led:
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
    global flashing_led
    flashing_led = False

def start_melody():
    """Play the Tokyo Drift melody in a loop."""
    print("Starting Tokyo Drift melody...")
    global playing_melody, speaker
    playing_melody = True
    
    def play_melody():
        # Play introduction once
        for note in listen_mus2:
            if not playing_melody:
                break
            speaker.play(note[0])
            sleep(note[1])
            speaker.stop()
            sleep(0.04)
        
        # Loop the main melody
        while playing_melody:
            for note in liten_mus:
                if not playing_melody:
                    break
                speaker.play(note[0])
                sleep(note[1])
                speaker.stop()
                sleep(0.04)
    
    threading.Thread(target=play_melody).start()
    print("Tokyo Drift melody started.")

def stop_melody():
    """Stop playing the Tokyo Drift melody."""
    print("Stopping Tokyo Drift melody...")
    global playing_melody, speaker
    playing_melody = False
    speaker.stop()
    print("Tokyo Drift melody stopped.")

def stop_all():
    """Turn off all IOs"""
    global flashing_led
    flashing_led = False
    red_led.off()
    blue_led.off()
    speaker.stop()
