import RPi.GPIO as GPIO
import time

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        while GPIO.input(self.DOUT) == 1:
            pass

        value = 0
        for _ in range(24):
            GPIO.output(self.PD_SCK, True)
            value = (value << 1) | GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)

        for _ in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        if value & 0x800000:
            value |= ~0xffffff

        return value

    def read_average(self, times=3):
        s = 0
        for _ in range(times):
            s += self.read()
        return s / times

    def tare(self):
        self.OFFSET = self.read_average()

    def get_weight(self, times=3):
        return (self.read_average(times) - self.OFFSET) / self.SCALE

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.1)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.1)
