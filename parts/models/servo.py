import pigpio
import time

class Servo(object):
    def __init__(self, pin):
        self.pi=pigpio.pi()
        self.pin=pin
        self.pi.set_servo_pulsewidth(pin, 2500)
    
    def open(self):
        self.pi.set_servo_pulsewidth(self.pin, 500)
