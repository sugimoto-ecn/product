from models import active_buzzer

class ActiveBuzzerController(object):
    def __init__(self , pin):
        self.buzzer = active_buzzer.ActiveBuzzer(pin)

    def on(self):
        self.buzzer.alerm()
    
    def off(self):
        self.buzzer.stop()
    
    def __del__(self):
        del self.buzzer