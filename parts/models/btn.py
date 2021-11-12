import RPi.GPIO as GPIO



class Btn(object):
    def __init__(self , pin): 
        print("init ntn")
        self.pin = pin
        self.status=False
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.change_sw_status, bouncetime=300)

    def change_sw_status(self, ev=None):
        print(self.status)
        self.status = not self.status
    
    def init_status(self):
        self.status=False