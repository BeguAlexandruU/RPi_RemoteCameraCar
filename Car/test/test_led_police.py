from lib.picozero import LED
from time import sleep

red = LED(29)
blue = LED(28)

while True:
    for _ in range(2):
        red.on()
        sleep(0.1)
        red.off()
        sleep(0.1)
    for _ in range(2):
        blue.on()
        sleep(0.1)
        blue.off()
        sleep(0.1)
    
