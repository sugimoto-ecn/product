from models import lcd_clock
from utils import time_format
import time


class ClockController(object):
    def __init__(self, alerm, sleep):
        self.alerm=alerm
        self.clock = lcd_clock.Lcd()
        self.sleep = sleep

    def show_current_time(self):
        current_time = time_format.current_time_format()
        self.clock.show_display(current_time["ymd"] , current_time["hms"])
    
    def show_alerm_time(self):
        self.clock.show_display("Alerm time:", self.alerm)
    
    def show_sleep_time(self):
        self.clock.show_display("sleep time:", self.sleep)

    def show_time(self):
        night = False
        current_time = time_format.current_time_format()
        print(current_time["hms"])
        if int(current_time["hms"][:2]) >= int(self.sleep[:2]) and int(current_time["hms"][3:5]) > int(self.sleep[3:5]):
            night = True
        if night == True:
            self.show_alerm_time()
        else:
            self.show_sleep_time()
        
        return night
    def change_alerm(self, new_val):
        self.alerm=new_val

    def change_seep(self, new_val):
        self.sleep=new_val

    def off(self):
        del self.clock