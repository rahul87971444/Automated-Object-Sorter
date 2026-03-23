import time
from hx711_no_setup import HX711
import RPi.GPIO as GPIO

# ------------------------
# GPIO PINS
# ------------------------
DOUT = 5
SCK  = 6

GPIO.setwarnings(False)

hx = HX711(DOUT, SCK)

# ------------------------
# STEP 1: TARE
# ------------------------
print("\nSTEP 1: REMOVE ALL WEIGHT FROM LOAD CELL")
print("Taring in 3 seconds...")
time.sleep(3)

hx.tare()
print("Tare completed successfully")

time.sleep(1)

# ------------------------
# STEP 2: 50 g CALIBRATION
# ------------------------
input("\nSTEP 2: PLACE 50 g WEIGHT and press ENTER")
time.sleep(2)

raw_50 = hx.get_weight(10)
print("Raw HX711 reading @ 50 g :", raw_50)

hx.power_down()
time.sleep(0.1)
hx.power_up()

# ------------------------
# STEP 3: 200 g CALIBRATION
# ------------------------
input("\nSTEP 3: REMOVE 50 g, PLACE 200 g WEIGHT and press ENTER")
time.sleep(2)

raw_200 = hx.get_weight(10)
print("Raw HX711 reading @ 200 g:", raw_200)

hx.power_down()
time.sleep(0.1)
hx.power_up()

# ------------------------
# STEP 4: CALCULATE SCALE FACTOR
# ------------------------
factor_50  = raw_50 / 50.0
factor_200 = raw_200 / 200.0

CAL_FACTOR = (factor_50 + factor_200) / 2.0

# ------------------------
# RESULTS
# ------------------------
print("\n=========== CALIBRATION DONE ===========")
print(f"Factor @ 50 g   : {factor_50:.4f}")
print(f"Factor @ 200 g  : {factor_200:.4f}")
print(f"\nFINAL CAL_FACTOR = {CAL_FACTOR:.4f}")
print("=======================================")

print("\n? Save FINAL CAL_FACTOR and use it in your measurement code")
