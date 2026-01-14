from lib.picozero import Speaker
from time import sleep


speaker = Speaker(0)


melody_introduction = ['a#4', 'a#4', 'a#4', 'a#4',]
durations_introduction = [4, 4, 4, 4]

melody = [
  # Motive principal (bar 1–2)
  'a#4', 'b4', 'd#5', 'a#4', 'a#4',
  'a#4', 'b4', 'd#5', 'a#4', 'a#4',
  'a#4', 'b4', 'd#5', 'a#4', 'a#4',
  'a#4', 'b4', 'd#5', 'f5', 'f5',
  'g#5', 'f#5', 'f5', 'd#5', 'd#5',
  'g#5', 'f#5', 'f5', 'd#5', 'd#5',
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
    

# Example output (first 10 notes)
# print(liten_mus)

try:
    for note in listen_mus2:
        speaker.play(note)
        sleep(0.04) 
    while(True):
      for note in liten_mus:
          speaker.play(note)
          sleep(0.04)
    
    
finally: # Turn speaker off if interrupted
    speaker.off()