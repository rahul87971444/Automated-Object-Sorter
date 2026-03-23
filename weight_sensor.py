import time
from hx711_no_setup import HX711
import RPi.GPIO as GPIO
from collections import deque

DOUT = 5
SCK  = 6

GPIO.setwarnings(False)

hx = HX711(DOUT, SCK)

print("Taring...")
time.sleep(2)
hx.tare()
print("Ready!")

CAL_FACTOR = 500   # <-- PUT YOUR VALUE HERE

FILTER_SIZE = 5
buffer = deque(maxlen=FILTER_SIZE)

def smooth(v):
    buffer.append(v)
    return sum(buffer) / len(buffer)

while True:
    raw = hx.get_weight(3)
    weight = raw / CAL_FACTOR
    weight = smooth(weight)

    if abs(weight) < 3:
        weight = 0

    print(f"Weight: {weight:.2f} g")
    time.sleep(0.3)
