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
        GPIO.output(self.pin , self.status)

    def stop(self):
        self.status = self.off
        GPIO.output(self.pin, self.status)
    
    def __del__(self):
        self.status = self.off
        GPIO.output(self.pin, self.status)