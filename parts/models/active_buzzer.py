import RPi.GPIO as GPIO
import time

class ActiveBuzzer(object):
    def __init__(self, pin):
        print("init buzzer")
        self.pin = pin
        self.off = GPIO.HIGH
        self.on = GPIO.LOW
        self.status = GPIO.HIGH
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=self.status)

    def alerm(self):
        self.status = self.on
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.pin , self.status)
        # count = 0
        # while True:
        # # Buzzer on (Beep)
        #     GPIO.output(self.pin , GPIO.LOW)
        #     time.sleep(0.08)
        #     # Buzzer off
        #     GPIO.output(self.pin , GPIO.HIGH)
        #     time.sleep(0.1)
        #     if count >= 4:
        #         time.sleep(0.5)
        #         count = 0


    def stop(self):
        self.status = self.off
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.pin, self.status)
    
    def __del__(self):
        self.status = self.off
        GPIO.output(self.pin, self.status)