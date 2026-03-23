import time
import board
import busio
from adafruit_pca9685 import PCA9685

# -----------------------------
# PCA9685 SETUP
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# -----------------------------
# SERVO CHANNEL MAPPING
# -----------------------------
BASE = 0
SHOULDER = 1
ELBOW = 2
WRIST  = 3
GRIPPER = 4

# -----------------------------
# SERVO PULSE LIMITS
# -----------------------------
MG90_MIN = 600
MG90_MAX = 2400

SG90_MIN = 500
SG90_MAX = 2400

# -----------------------------
# SERVO CONTROL FUNCTIONS
# -----------------------------
def set_mg90(channel, angle):
    pulse = MG90_MIN + (angle / 180.0) * (MG90_MAX - MG90_MIN)
    duty = int((pulse / 1000000.0) * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty

def set_sg90(channel, angle):
    pulse = SG90_MIN + (angle / 180.0) * (SG90_MAX - SG90_MIN)
    duty = int((pulse / 1000000.0) * pca.frequency * 65535)
    pca.channels[channel].duty_cycle = duty

# -----------------------------
# ARM POSITIONS
# -----------------------------
def arm_home():
    set_mg90(BASE, 90)
    set_mg90(SHOULDER, 90)
    set_mg90(ELBOW, 90)
    set_sg90(WRIST, 90)
    set_sg90(GRIPPER, 60)
    time.sleep(1)

def move_to_object():
    set_mg90(BASE, 90)
    time.sleep(1)
    set_mg90(SHOULDER, 60)
    time.sleep(1)
    set_mg90(ELBOW, 165)
    set_sg90(WRIST, 100)
    time.sleep(1)

def grab_object():
    set_sg90(GRIPPER, 25)
    time.sleep(1)

def lift_object():
    set_mg90(SHOULDER,60)
    set_mg90(ELBOW, 90)
    time.sleep(1)

def place_object():
    set_mg90(BASE, 150)
    time.sleep(1)
    set_mg90(ELBOW, 130)
    time.sleep(1)
    set_mg90(SHOULDER, 80)
    time.sleep(1)

    set_sg90(GRIPPER, 60)
    time.sleep(1)

# -----------------------------
# MAIN PROGRAM
# -----------------------------
try:
    arm_home()
    move_to_object()
    grab_object()
    lift_object()
    place_object()
    arm_home()

except KeyboardInterrupt:
    pass

finally:
    pca.deinit()
